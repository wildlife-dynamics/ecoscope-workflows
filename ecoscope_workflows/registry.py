"""Task and de/serialization function registry.
Can be mutated with entry points.
"""

import importlib

# from importlib.metadata import entry_points
from typing import Annotated, Any, Callable, get_args

import ruamel.yaml
import pandera as pa
from pydantic import BaseModel, FieldSerializationInfo, TypeAdapter, field_serializer
from pydantic.functional_validators import AfterValidator

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.serde import gpd_from_parquet_uri

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


def _rsplit_importable_reference(reference: str) -> list[str]:
    """Splits enclosing module and object name from importable reference."""
    return reference.rsplit(".", 1)


def _validate_importable_reference(reference: str):
    """Without importing the reference, does the best we can to ensure that it will be importable."""
    parts = _rsplit_importable_reference(reference)
    assert (
        len(parts) == 2
    ), f"{reference} is not a valid importable reference, must be a dotted string."
    assert (
        parts[1].isidentifier()
    ), f"{parts[1]} is not a valid Python identifier, it will not be importable."
    assert all(
        [module_part.isidentifier() for module_part in parts[0].split(".")]
    ), f"{parts[0]} is not a valid Python module path, it will not be importable."
    return reference


ImportableReference = Annotated[str, AfterValidator(_validate_importable_reference)]


class KnownTask(BaseModel):
    importable_reference: ImportableReference
    # tags: list[str]
    operator: KubernetesPodOperator
    testing_implementation: ImportableReference | None = None

    @field_serializer("importable_reference")
    def serialize_importable_reference(self, v: Any, info: FieldSerializationInfo):
        context: dict = info.context
        if context:
            testing = context.get("testing", False)
            if testing:
                return {
                    "module": self.testing_module,
                    "function": self.testing_function,
                }
        return {"module": self.module, "function": self.function}

    @property
    def module(self) -> str:
        return _rsplit_importable_reference(self.importable_reference)[0]

    @property
    def testing_module(self) -> str | None:
        return (
            _rsplit_importable_reference(self.testing_implementation)[0]
            if self.testing_implementation
            else None
        )

    @property
    def function(self) -> str:
        return _rsplit_importable_reference(self.importable_reference)[1]

    @property
    def testing_function(self) -> str | None:
        return (
            _rsplit_importable_reference(self.testing_implementation)[1]
            if self.testing_implementation
            else None
        )

    def _import_func(self) -> Callable:
        # imports the distributed function. we will need to be clear in docs about what imports are
        # allowed at top level (ecoscope_workflows, pydantic, pandera, pandas) and which imports
        # must be deferred to function body (geopandas, ecoscope itself, etc.).
        # maybe we can also enforce this programmatically.
        mod = importlib.import_module(self.module)
        func = getattr(mod, self.function)
        assert isinstance(
            func, distributed
        ), f"{self.importable_reference} is not `@distributed`"
        return func.func

    def parameters_jsonschema(self, omit_args: list[str] | None = None) -> dict:
        func = self._import_func()
        # NOTE: SurfacesDescriptionSchema is a workaround for https://github.com/pydantic/pydantic/issues/9404
        # Once that issue is closed, we can remove SurfaceDescriptionSchema and use the default schema_generator.
        schema = TypeAdapter(func).json_schema(
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
        func = self._import_func()
        return {
            arg: get_args(annotation)
            for arg, annotation in func.__annotations__.items()
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
        importable_reference="ecoscope_workflows.tasks.python.io.get_subjectgroup_observations",
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
        testing_implementation="ecoscope_workflows.testing.tasks.python.io.get_subjectgroup_observations",
    ),
    "process_relocations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.python.preprocessing.process_relocations",
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
        importable_reference="ecoscope_workflows.tasks.python.preprocessing.relocations_to_trajectory",
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
        importable_reference="ecoscope_workflows.tasks.python.analysis.calculate_time_density",
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
