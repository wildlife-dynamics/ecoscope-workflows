"""Task and de/serialization function registry.
Can be mutated with entry points.
"""
from pydantic import BaseModel


class KnownTask(BaseModel):
    image: str
    # pod_name: str
    task_import: str
    # tags: list[str]


known_tasks = {
    "get_earthranger_subjectgroup_observations": KnownTask(
        image="ecoscope:0.1.7",
        task_import="ecoscope_workflows.tasks.python.io.get_subjectgroup_observations",
    ),
}
