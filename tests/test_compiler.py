from textwrap import dedent

import yaml

from ecoscope_workflows.compiler import DagCompiler, Spec, TaskInstance
from ecoscope_workflows.registry import KnownTask, known_tasks


def test_task_instance_known_task_parsing():
    task_name = "get_subjectgroup_observations"
    ti = TaskInstance(known_task_name=task_name)
    assert isinstance(ti.known_task, KnownTask)
    assert ti.known_task == known_tasks[task_name]


def test_dag_compiler_from_spec():
    spec_str = dedent(
        """\s
    name: calculate_time_density
    cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
    tasks:
        get_subjectgroup_observations: {}
        process_relocations:
            observations: get_subjectgroup_observations
    """
    )
    spec_dict = yaml.safe_load(spec_str)
    spec = Spec.from_spec_file(spec=spec_dict)
    dc = DagCompiler(spec=spec)
    assert isinstance(dc.spec.tasks["get_subjectgroup_observations"], TaskInstance)
