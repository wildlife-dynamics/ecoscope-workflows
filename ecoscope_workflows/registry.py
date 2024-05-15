"""Task and de/serialization function registry.
Can be mutated with entry points.
"""

from ecoscope_workflows.configuration import TaskRegistration

known_tasks = {
    "ecoscope_workflows.tasks.python.io.get_subjectgroup_observations": TaskRegistration(
        image="ecoscope:0.1.7",
    ),
}
