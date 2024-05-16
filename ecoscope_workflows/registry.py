"""Task and de/serialization function registry.
Can be mutated with entry points.
"""
from pydantic import BaseModel, TypeAdapter, computed_field

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.jsonschema import SurfacesDescriptionSchema
from ecoscope_workflows.importstring import import_item


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

    @computed_field
    @property
    def parameters_jsonschema(self) -> dict:
        # imports the distributed function. we will need to be clear in docs about what imports are
        # allowed at top level (ecoscope_workflows, pydantic, pandera, pandas) and which imports
        # must be deferred to function body (geopandas, ecoscope itself, etc.).
        # maybe we can also enforce this programmatically.
        func = import_item(self.importable_reference)
        assert isinstance(func, distributed), f"{self.importable_reference} is not `@distributed`"
        return TypeAdapter(func.func).json_schema(schema_generator=SurfacesDescriptionSchema)


known_tasks = {
    "get_earthranger_subjectgroup_observations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.python.io.get_subjectgroup_observations",
        operator=KubernetesPodOperator(
            image="ecoscope:0.1.7",
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
            image="ecoscope:0.1.7",
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
