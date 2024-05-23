"""Task and de/serialization function registry.
Can be mutated with entry points.
"""

# from importlib.metadata import entry_points
from typing import Annotated, Any, get_args

import ruamel.yaml
import pandera as pa
from pydantic import BaseModel, FieldSerializationInfo, TypeAdapter, field_serializer
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.util import (
    import_distributed_task_from_reference,
    rsplit_importable_reference,
    validate_importable_reference,
)

# def process_entries():
#     if entry_points is not None:
#         eps = entry_points()
#         if hasattr(eps, "select"):  # Python 3.10+ / importlib_metadata >= 3.9.0
#             specs = eps.select(group="fsspec.specs")
#         else:
#             specs = eps.get("ecoscope-workflows.tasks", [])
#             for spec in specs:
#                 known_tasks[spec.name] = spec

# process_entries()


class KubernetesPodOperator(BaseModel):
    image: str
    name: str  # This is the *pod* name
    # TODO: BaseModel for resouces
    # api reference: https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html#airflow.providers.cncf.kubernetes.operators.pod.KubernetesPodOperator:~:text=by%20labels.%20(templated)-,container_resources,-(kubernetes.client
    container_resources: dict


ImportableReference = Annotated[str, AfterValidator(validate_importable_reference)]


class KnownTask(BaseModel):
    importable_reference: ImportableReference
    # tags: list[str]
    operator: KubernetesPodOperator

    @field_serializer("importable_reference")
    def serialize_importable_reference(self, v: Any, info: FieldSerializationInfo):
        context: dict = info.context
        testing = context.get("testing", False)
        mocks = context.get("mocks", [])
        return {
            "module": self.module,
            "function": self.function,
            "statement": (
                (
                    # if this is a testing context, and a mock was requested:
                    f"{self.function} = create_distributed_task_magicmock(  # 🧪\n"
                    f"    anchor='{self.module}',  # 🧪\n"
                    f"    func_name='{self.function}',  # 🧪\n"
                    ")  # 🧪"
                )
                if testing and self.function in mocks
                # but in most cases just import the function in a normal way
                else f"from {self.module} import {self.function}"
            ),
        }

    @property
    def sample_data_fname(self) -> str:
        return (
            f"{self.function.replace('_', '-')}.parquet"  # FIXME: might not be parquet
        )

    @property
    def module(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[0]

    @property
    def function(self) -> str:
        return rsplit_importable_reference(self.importable_reference)[1]

    def parameters_jsonschema(self, omit_args: list[str] | None = None) -> dict:
        func = import_distributed_task_from_reference(self.module, self.function)
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
        func = import_distributed_task_from_reference(self.module, self.function)
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
}

known_deserializers = {
    pa.typing.DataFrame: gpd_from_parquet_uri,
}
