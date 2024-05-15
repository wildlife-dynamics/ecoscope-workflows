from ecoscope_workflows.configuration import KnownTask, TaskInstance
from ecoscope_workflows.registry import known_tasks


def test_task_instance_known_task_parsing():
    task_name = "get_earthranger_subjectgroup_observations"
    ti = TaskInstance(known_task=task_name)
    assert isinstance(ti.known_task, KnownTask)
    assert ti.known_task == known_tasks[task_name]
