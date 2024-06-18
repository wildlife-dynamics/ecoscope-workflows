"""Task and deserialization function registry. Can be extended on a per-session basis with
entry points. This design is heavily inspired by the `fsspec` package's `registry` module,
to which we owe a debt of gratitude.
"""

import ast
import types
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from inspect import getmembers, getsource, ismodule
from typing import Annotated, Any, Generator, get_args

import ruamel.yaml
import pandera as pa
from pydantic import (
    BaseModel,
    Field,
    FieldSerializationInfo,
    TypeAdapter,
    computed_field,
    field_serializer,
)
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.annotations import (
    JsonSerializableDataFrameModel,
    is_client,
    connection_from_client,
)
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
        # FIXME: handle name collisions, which would currently result in overwriting
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
                    f"{self.function} = create_distributed_task_magicmock(  # 🧪\n"
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
    def task(self) -> DistributedTask:
        return import_distributed_task_from_reference(self.anchor, self.function)

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

    @property
    def client_model_fields(self) -> dict:
        cmf = {}
        for k, v in self.params_annotations.items():
            if is_client(v):
                conn = connection_from_client(v)
                cmf[k] = {
                    "type": conn.__name__,
                    "fields": conn.model_fields,
                }
        return cmf

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

    def parameters_annotation_yaml_str(self, omit_args: list[str] | None = None) -> str:
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml_str = f"{self.function}:\n"
        for line in self._iter_parameters_annotation(
            fmt="  {arg}:   # {param}\n",
            omit_args=omit_args,
        ):
            yaml_str += line
        _ = yaml.load(yaml_str)
        return yaml_str

    def parameters_notebook(self, omit_args: list[str] | None = None) -> str:
        params = ""
        for line in self._iter_parameters_annotation(
            fmt="{arg} = ...\n",
            omit_args=omit_args,
        ):
            params += line
        return params

    @property
    def _ast_parsed_function_def(self) -> ast.FunctionDef:
        source = getsource(self.task)
        module = ast.parse(source)
        function_def = module.body[0]
        assert isinstance(function_def, ast.FunctionDef)
        return function_def

    @computed_field
    def source_body(self) -> str:
        return "\n".join(
            ast.unparse(stmt)
            for stmt in self._ast_parsed_function_def.body
            if not isinstance(stmt, ast.Return)
        )

    @computed_field
    def source_return(self) -> str:
        return_stmt = [
            stmt
            for stmt in self._ast_parsed_function_def.body
            if isinstance(stmt, ast.Return)
        ][0]
        return ast.unparse(return_stmt).replace("return ", "")


_known_tasks = collect_task_entries()  # internal, mutable
known_tasks = types.MappingProxyType(_known_tasks)  # external, immutable


known_deserializers = {
    pa.typing.DataFrame: gpd_from_parquet_uri,
}
