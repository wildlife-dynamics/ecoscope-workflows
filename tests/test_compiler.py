from textwrap import dedent

import pytest
import yaml
from pydantic_core import ValidationError

from ecoscope_workflows.compiler import DagCompiler, Spec, TaskInstance
from ecoscope_workflows.registry import KnownTask, known_tasks


def test_task_instance_known_task_parsing():
    task_name = "get_subjectgroup_observations"
    kws = {"name": "Get Subjectgroup Observations", "id": "obs"}
    ti = TaskInstance(task=task_name, **kws)
    assert isinstance(ti.known_task, KnownTask)
    assert ti.known_task == known_tasks[task_name]


def test_dag_compiler_from_spec():
    s = dedent(
        """\
        name: calculate_time_density
        cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
            with: {}
          - name: Process Relocations
            id: relocs
            task: process_relocations
            with:
              observations: ${{ get_subjectgroup_observations.return }}
        """
    )
    spec = Spec(**yaml.safe_load(s))
    dc = DagCompiler(spec=spec)
    assert isinstance(dc.spec.workflow[0], TaskInstance)


def test_extra_forbid_raises():
    s = dedent(
        # this workflow has an extra key, `observations` in the second task
        # this is a mistake, as this should be nested under a `with` block
        """\
        name: calculate_time_density
        cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
            with: {}
          - name: Process Relocations
            id: relocs
            task: process_relocations
            observations: ${{ get_subjectgroup_observations }}
        """
    )
    with pytest.raises(ValidationError):
        _ = Spec(**yaml.safe_load(s))
