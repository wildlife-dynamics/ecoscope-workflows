"""Task and de/serialization function registry.
Can be mutated with entry points.
"""
import importlib
# from importlib.metadata import entry_points
from typing import Callable, get_args

import ruamel.yaml
from pydantic import BaseModel, TypeAdapter, computed_field

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema

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


class KnownTask(BaseModel):
    # pod_name: str
    importable_reference: str
    # tags: list[str]
    operator: KubernetesPodOperator

    @property
    def _importable_reference_parts(self):
        # TODO: assert rsplit len = 2 on __init__
        return self.importable_reference.rsplit(".", 1)

    @computed_field
    @property
    def module(self) -> str:
        return self._importable_reference_parts[0]
    
    @computed_field
    @property
    def function(self) -> str:
        return self._importable_reference_parts[1]

    def _import_func(self) -> Callable:
        # imports the distributed function. we will need to be clear in docs about what imports are
        # allowed at top level (ecoscope_workflows, pydantic, pandera, pandas) and which imports
        # must be deferred to function body (geopandas, ecoscope itself, etc.).
        # maybe we can also enforce this programmatically.
        mod = importlib.import_module(self.module)
        func = getattr(mod, self.function)
        assert isinstance(func, distributed), f"{self.importable_reference} is not `@distributed`"
        return func.func

    def parameters_jsonschema(self) -> dict:
        func = self._import_func()
        return TypeAdapter(func).json_schema(schema_generator=SurfacesDescriptionSchema)

    @property
    def parameters_annotation(self) -> dict[str, list]:
        func = self._import_func()
        return {
            arg: get_args(annotation) for arg, annotation in func.__annotations__.items()
        }

    def parameters_annotation_yaml_str(self) -> str:
        yaml = ruamel.yaml.YAML(typ="rt")
        yaml_str = f"{self.function}:\n"
        for arg, param in self.parameters_annotation.items():
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
            }
        ),
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
            }
        ),
    ),
}
