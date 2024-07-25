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
          - name: Process Relocations
            id: relocs
            task: process_relocations
            observations: ${{ get_subjectgroup_observations }}
        """
    )
    with pytest.raises(ValidationError):
        _ = Spec(**yaml.safe_load(s))


@pytest.mark.parametrize(
    "invalid_id, raises_match",
    [
        ("1obs", "`1obs` is not a valid python identifier."),
        ("obs-1", "`obs-1` is not a valid python identifier."),
        ("obs 1", "`obs 1` is not a valid python identifier."),
        ("with", "`with` is a python keyword."),
        ("return", "`return` is a python keyword."),
        ("print", "`print` is a built-in python function."),
        ("map", "`map` is a built-in python function."),
        ("list", "`list` is a built-in python function."),
        # TODO: collision with known task names
    ],
)
def test_invalid_id_raises(invalid_id: str, raises_match: str):
    s = dedent(
        f"""\
        name: calculate_time_density
        cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
        workflow:
          - name: Get Subjectgroup Observations
            id: {invalid_id}
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(ValidationError, match=raises_match):
        _ = Spec(**yaml.safe_load(s))


@pytest.mark.parametrize(
    "task, valid_known_task_name",
    [
        ("get_subjectgroup_observations", True),
        ("fetch_subject_obs", False),
        ("process_relocations", True),
        ("preproc_relocs", False),
    ],
)
def test_invalid_known_task_name_raises(task: str, valid_known_task_name: bool):
    s = dedent(
        f"""\
        name: calculate_time_density
        cache_root: gcs://my-bucket/ecoscope/cache/dag-runs
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: {task}
        """
    )
    if valid_known_task_name:
        spec = Spec(**yaml.safe_load(s))
        assert spec.workflow[0].known_task == known_tasks[task]
    else:
        with pytest.raises(
            ValidationError, match=f"`{task}` is not a registered known task name."
        ):
            _ = Spec(**yaml.safe_load(s))
