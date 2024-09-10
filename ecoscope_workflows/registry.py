"""Task and deserialization function registry. Can be extended on a per-session basis with
entry points. This design is heavily inspired by the `fsspec` package's `registry` module,
to which we owe a debt of gratitude.
"""

import types
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from inspect import getmembers, ismodule
from typing import Annotated, Any, Generator, get_args

import ruamel.yaml
from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    TypeAdapter,
    field_serializer,
)
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.annotations import (
    JsonSerializableDataFrameModel,
)
from ecoscope_workflows.connections import EarthRangerConnection
from ecoscope_workflows.decorators import SyncTask
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.util import (
    import_task_from_reference,
    rsplit_importable_reference,
    validate_importable_reference,
)


@dataclass
class _KnownTaskArgs:
    name: str
    anchor: str
    tags: list[str]


def recurse_into_tasks(
    module: types.ModuleType,
) -> Generator[_KnownTaskArgs, None, None]:
    """Recursively yield `@task` names from the given module (i.e. package)."""
    for name, obj in [
        m for m in getmembers(module) if not m[0].startswith(("__", "_"))
    ]:
        if isinstance(obj, SyncTask):
            yield _KnownTaskArgs(
                name=name,
                anchor=module.__name__,
                tags=obj.tags or [],
            )
        elif ismodule(obj):
            yield from recurse_into_tasks(obj)
        elif issubclass(obj, JsonSerializableDataFrameModel):
            continue
        else:
            raise ValueError(f"Unexpected member {obj} in module {module}")


def collect_task_entries() -> dict[str, "KnownTask"]:
    eps = entry_points()
    assert hasattr(eps, "select")  # Python >= 3.10
    ecoscope_workflows_eps = eps.select(group="ecoscope_workflows")
    known_tasks: dict[str, "KnownTask"] = {}
    for ep in ecoscope_workflows_eps:
        # a bit redundant with `util.import_task_from_reference`
        root_pkg_name, tasks_pkg_name = ep.value.rsplit(".", 1)
        assert "." not in root_pkg_name, (
            "Tasks must be top-level in root (e.g. `pkg.tasks`, not `pkg.foo.tasks`). "
            f"Got: `{root_pkg_name}.{tasks_pkg_name}`"
        )
        root = import_module(root_pkg_name)
        tasks_module = getattr(root, tasks_pkg_name)
        known_task_args = [t for t in recurse_into_tasks(tasks_module)]
        # FIXME: handle name collisions, which would currently result in overwriting
        known_tasks |= {
            kta.name: KnownTask(
                # TODO: since we are assembling the importable reference here,
                # perhaps the fact that anchor and function names are properties
                # of KnownTask is strange? Maybe we should just pass them directly.
                importable_reference=f"{kta.anchor}.{kta.name}",
                tags=[TaskTag(t) for t in kta.tags],
            )
            for kta in known_task_args
        }
    return known_tasks


ImportableReference = Annotated[str, AfterValidator(validate_importable_reference)]


class TaskTag(str, Enum):
    io = "io"


class KnownTask(BaseModel):
    importable_reference: ImportableReference
    tags: list[TaskTag] = Field(default_factory=list)

    @field_serializer("importable_reference")
    def serialize_importable_reference(self, v: Any, info: FieldSerializationInfo):
        context: dict = info.context if info.context else {}
        testing = context.get("testing", False)
        mocks = context.get("mocks", [])
        omit_args = context.get("omit_args", [])
        return {
            "anchor": self.anchor,
            "function": self.function,
            "statement": (
                (
                    # if this is a testing context, and a mock was requested:
                    f"{self.function} = create_task_magicmock(  # 🧪\n"
                    f"    anchor='{self.anchor}',  # 🧪\n"
                    f"    func_name='{self.function}',  # 🧪\n"
                    ")  # 🧪"
                )
                if testing and self.function in mocks
                # but in most cases just import the function in a normal way
                else f"from {self.anchor} import {self.function}"
            ),
            "params_notebook": self.parameters_notebook(omit_args=omit_args),
        }

    @property
    def anchor(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[0]

    @property
    def function(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[1]

    @property
    def task(self) -> SyncTask:
        return import_task_from_reference(self.anchor, self.function)

    def parameters_jsonschema(self, omit_args: list[str] | None = None) -> dict:
        # NOTE: SurfacesDescriptionSchema is a workaround for https://github.com/pydantic/pydantic/issues/9404
        # Once that issue is closed, we can remove SurfaceDescriptionSchema and use the default schema_generator.
        schema = TypeAdapter(
            self.task.func,
            config={"arbitrary_types_allowed": True},
        ).json_schema(schema_generator=SurfacesDescriptionSchema)
        if omit_args:
            schema["properties"] = {
                arg: schema["properties"][arg]
                for arg in schema["properties"]
                if arg not in omit_args
            }
            schema["required"] = [
                arg for arg in schema["required"] if arg not in omit_args
            ]
        return schema

    @property
    def params_annotations(self) -> dict[str, tuple]:
        return {
            arg: annotation
            for arg, annotation in self.task.func.__annotations__.items()
        }

    @property
    def params_annotations_args(self) -> dict[str, tuple]:
        return {
            arg: get_args(annotation)
            for arg, annotation in self.params_annotations.items()
        }

    def _iter_parameters_annotation(
        self,
        fmt: str,  # TODO: is there a stricter type for formatter w/ params?
        omit_args: list[str] | None = None,
    ) -> Generator[str, None, None]:
        for arg, param in {
            k: v
            for k, v in self.params_annotations_args.items()
            if k not in (omit_args or [])
        }.items():
            yield fmt.format(arg=arg, param=param)

    def parameters_annotation_yaml_str(
        self,
        title: str,
        description: str,
        omit_args: list[str] | None = None,
    ) -> str:
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml_str = f"{description}\n{title}:\n"
        for line in self._iter_parameters_annotation(
            fmt="  {arg}:   # {param}\n",
            omit_args=omit_args,
        ):
            yaml_str += line
        _ = yaml.load(yaml_str)
        return yaml_str + "\n"

    def parameters_notebook(self, omit_args: list[str] | None = None) -> str:
        params = "dict(\n"
        for line in self._iter_parameters_annotation(
            fmt="    {arg}=...,\n",
            omit_args=omit_args,
        ):
            params += line
        params += ")"
        return params


_known_tasks = collect_task_entries()  # internal, mutable
known_tasks = types.MappingProxyType(_known_tasks)  # external, immutable

known_connections = {
    conn.__ecoscope_connection_type__: conn for conn in (EarthRangerConnection,)
}
