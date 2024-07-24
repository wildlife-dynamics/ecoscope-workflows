from textwrap import dedent

import pytest
import yaml

from ecoscope_workflows.compiler import DagCompiler, Spec, TaskInstance
from ecoscope_workflows.registry import KnownTask, known_tasks


def test_task_instance_known_task_parsing():
    task_name = "get_subjectgroup_observations"
    ti = TaskInstance(known_task_name=task_name)
    assert isinstance(ti.known_task, KnownTask)
    assert ti.known_task == known_tasks[task_name]


@pytest.fixture
def spec_dict() -> dict:
    spec_str = dedent(
        """\
        name: calculate_time_density
        cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
        workflow:
          - task: get_subjectgroup_observations
            with: {}
          - task: process_relocations
            with:
              observations: get_subjectgroup_observations
        """
    )
    return yaml.safe_load(spec_str)


def test_dag_compiler_from_spec(spec_dict: dict):
    spec = Spec(**spec_dict)
    dc = DagCompiler(spec=spec)
    assert isinstance(dc.spec.workflow[0], TaskInstance)
