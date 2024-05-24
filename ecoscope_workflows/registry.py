"""Task and de/serialization function registry.
Can be mutated with entry points.
"""

import types
from enum import Enum
from importlib import import_module
from importlib.metadata import entry_points
from inspect import getmembers, ismodule
from typing import Annotated, Any, get_args

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

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.util import (
    import_distributed_task_from_reference,
    rsplit_importable_reference,
    validate_importable_reference,
)


def recurse_into_tasks(module: types.ModuleType):
    """Recursively yield `@distributed` task names from the given module (i.e. package)."""
    for name, obj in [
        m for m in getmembers(module) if not m[0].startswith(("__", "_"))
    ]:
        if isinstance(obj, distributed):
            yield name  # FIXME: return full `importable_reference`
        elif ismodule(obj):
            yield from recurse_into_tasks(obj)
        else:
            raise ValueError(f"Unexpected member {obj} in module {module}")


def process_entries():
    eps = entry_points()
    assert hasattr(eps, "select")  # Python >= 3.10
    ecoscope_workflows_eps = eps.select(group="ecoscope_workflows")
    for ep in ecoscope_workflows_eps:
        # a bit redundant with `util.import_distributed_task_from_reference`
        root_pkg_name, tasks_pkg_name = ep.value.rsplit(".", 1)
        assert "." not in root_pkg_name, (
            "Tasks must be top-level in root (e.g. `pkg.tasks`, not `pkg.foo.tasks`). "
            f"Got: `{root_pkg_name}.{tasks_pkg_name}`"
        )
        root = import_module(root_pkg_name)
        tasks = getattr(root, tasks_pkg_name)  # circular import
        # members = [m for m in getmembers(tasks) if not m[0].startswith("__")]

        # register_known_task(task.load())
        # breakpoint()


process_entries()


class KubernetesPodOperator(BaseModel):
    image: str
    name: str  # This is the *pod* name
    # TODO: BaseModel for resouces
    # api reference: https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html#airflow.providers.cncf.kubernetes.operators.pod.KubernetesPodOperator:~:text=by%20labels.%20(templated)-,container_resources,-(kubernetes.client
    container_resources: dict


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


known_tasks = {
    "get_subjectgroup_observations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.io.get_subjectgroup_observations",
        tags=[TaskTag.io],
        operator=KubernetesPodOperator(
            image="ecoscope-workflows:latest",
            name="pod",  # TODO: defer assignment of this?
            container_resources={
                "request_memory": "128Mi",
                "request_cpu": "500m",
                "limit_memory": "500Mi",
                "limit_cpu": 1,
            },
        ),
    ),
    "process_relocations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.preprocessing.process_relocations",
        operator=KubernetesPodOperator(
            image="ecoscope-workflows:latest",
            name="pod",  # TODO: defer assignment of this?
            container_resources={
                "request_memory": "128Mi",
                "request_cpu": "500m",
                "limit_memory": "500Mi",
                "limit_cpu": 1,
            },
        ),
    ),
    "relocations_to_trajectory": KnownTask(
        importable_reference="ecoscope_workflows.tasks.preprocessing.relocations_to_trajectory",
        operator=KubernetesPodOperator(
            image="ecoscope-workflows:latest",
            name="pod",  # TODO: defer assignment of this?
            container_resources={
                "request_memory": "128Mi",
                "request_cpu": "500m",
                "limit_memory": "500Mi",
                "limit_cpu": 1,
            },
        ),
    ),
    "calculate_time_density": KnownTask(
        importable_reference="ecoscope_workflows.tasks.analysis.calculate_time_density",
        operator=KubernetesPodOperator(
            image="ecoscope-workflows:latest",
            name="pod",  # TODO: defer assignment of this?
            container_resources={
                "request_memory": "128Mi",
                "request_cpu": "500m",
                "limit_memory": "500Mi",
                "limit_cpu": 1,
            },
        ),
    ),
    "draw_ecomap": KnownTask(
        importable_reference="ecoscope_workflows.tasks.results.draw_ecomap",
        operator=KubernetesPodOperator(
            image="ecoscope-workflows:latest",
            name="pod",  # TODO: defer assignment of this?
            container_resources={
                "request_memory": "128Mi",
                "request_cpu": "500m",
                "limit_memory": "500Mi",
                "limit_cpu": 1,
            },
        ),
    ),
}

known_deserializers = {
    pa.typing.DataFrame: gpd_from_parquet_uri,
}


def register_known_task(known_task_kws: dict):
    print(known_task_kws)
