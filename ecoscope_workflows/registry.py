"""Task and de/serialization function registry.
Can be mutated with entry points.
"""
from pydantic import BaseModel


class KubernetesPodOperator(BaseModel):
    image: str
    name: str  # This is the *pod* name


class KnownTask(BaseModel):
    # pod_name: str
    importable_reference: str
    # tags: list[str]
    operator: KubernetesPodOperator



known_tasks = {
    "get_earthranger_subjectgroup_observations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.python.io.get_subjectgroup_observations",
        operator=KubernetesPodOperator(
            image="ecoscope:0.1.7",
            name="pod",  # TODO: defer assignment of this?
        )
    ),
}
