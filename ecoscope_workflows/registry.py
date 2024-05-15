"""Task and de/serialization function registry.
Can be mutated with entry points.
"""
from pydantic import BaseModel


class KnownTask(BaseModel):
    # pod_name: str
    importable_reference: str
    # tags: list[str]
    image: str


known_tasks = {
    "get_earthranger_subjectgroup_observations": KnownTask(
        importable_reference="ecoscope_workflows.tasks.python.io.get_subjectgroup_observations",
        image="ecoscope:0.1.7",
    ),
}
