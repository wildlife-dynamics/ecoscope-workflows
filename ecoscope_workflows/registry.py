"""Task and de/serialization function registry.
Can be mutated with entry points.
"""

import types
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from inspect import getmembers, ismodule
from typing import Annotated, Any, Generator, get_args

import ruamel.yaml
import pandera as pa
from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    TypeAdapter,
    field_serializer,
)
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.annotations import JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import DistributedTask
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.operators import KubernetesPodOperator
from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.util import (
    import_distributed_task_from_reference,
    rsplit_importable_reference,
    validate_importable_reference,
)


@dataclass
class _KnownTaskArgs:
    name: str
    anchor: str
    operator_kws: dict
    tags: list[str]


def recurse_into_tasks(
    module: types.ModuleType,
) -> Generator[_KnownTaskArgs, None, None]:
    """Recursively yield `@distributed` task names from the given module (i.e. package)."""
    for name, obj in [
        m for m in getmembers(module) if not m[0].startswith(("__", "_"))
    ]:
        if isinstance(obj, DistributedTask):
            yield _KnownTaskArgs(
                name=name,
                anchor=module.__name__,
                operator_kws=obj.operator_kws.model_dump(),
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
        # a bit redundant with `util.import_distributed_task_from_reference`
        root_pkg_name, tasks_pkg_name = ep.value.rsplit(".", 1)
        assert "." not in root_pkg_name, (
            "Tasks must be top-level in root (e.g. `pkg.tasks`, not `pkg.foo.tasks`). "
            f"Got: `{root_pkg_name}.{tasks_pkg_name}`"
        )
        root = import_module(root_pkg_name)
        tasks_module = getattr(root, tasks_pkg_name)
        known_task_args = [t for t in recurse_into_tasks(tasks_module)]
        known_tasks |= {
            kta.name: KnownTask(
                # TODO: since we are assembling the importable reference here,
                # perhaps the fact that anchor and function names are properties
                # of KnownTask is strange? Maybe we should just pass them directly.
                importable_reference=f"{kta.anchor}.{kta.name}",
                operator=KubernetesPodOperator(**kta.operator_kws),
                tags=kta.tags,
            )
            for kta in known_task_args
        }
    return known_tasks


ImportableReference = Annotated[str, AfterValidator(validate_importable_reference)]


class TaskTag(str, Enum):
    io = "io"


class KnownTask(BaseModel):
    importable_reference: ImportableReference
    operator: KubernetesPodOperator
    tags: list[TaskTag] = Field(default_factory=list)

    @field_serializer("importable_reference")
    def serialize_importable_reference(self, v: Any, info: FieldSerializationInfo):
        context: dict = info.context
        testing = context.get("testing", False)
        mocks = context.get("mocks", [])
        return {
            "anchor": self.anchor,
            "function": self.function,
            "statement": (
                (
                    # if this is a testing context, and a mock was requested:
                    f"{self.function} = create_distributed_task_magicmock(  # 🧪\n"
                    f"    anchor='{self.anchor}',  # 🧪\n"
                    f"    func_name='{self.function}',  # 🧪\n"
                    ")  # 🧪"
                )
                if testing and self.function in mocks
                # but in most cases just import the function in a normal way
                else f"from {self.anchor} import {self.function}"
            ),
        }

    @property
    def anchor(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[0]

    @property
    def function(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[1]

    def parameters_jsonschema(self, omit_args: list[str] | None = None) -> dict:
        func = import_distributed_task_from_reference(self.anchor, self.function)
        # NOTE: SurfacesDescriptionSchema is a workaround for https://github.com/pydantic/pydantic/issues/9404
        # Once that issue is closed, we can remove SurfaceDescriptionSchema and use the default schema_generator.
        schema = TypeAdapter(func.func).json_schema(
            schema_generator=SurfacesDescriptionSchema
        )
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
    def parameters_annotation(self) -> dict[str, tuple]:
        func = import_distributed_task_from_reference(self.anchor, self.function)
        return {
            arg: get_args(annotation)
            for arg, annotation in func.func.__annotations__.items()
        }

    def parameters_annotation_yaml_str(self, omit_args: list[str] | None = None) -> str:
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml_str = f"{self.function}:\n"
        for arg, param in self.parameters_annotation.items():
            if omit_args and arg in omit_args:
                continue  # skip this arg
            yaml_str += f"  {arg}:   # {param}\n"
        _ = yaml.load(yaml_str)
        return yaml_str


known_tasks = collect_task_entries()

known_deserializers = {
    pa.typing.DataFrame: gpd_from_parquet_uri,
}
