import re
from textwrap import dedent

import pytest
import yaml
from pydantic_core import ValidationError

from ecoscope_workflows.compiler import DagCompiler, Spec, TaskInstance, TaskIdVariable
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
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
              observations: ${{ workflow.obs.return }}
        """
    )
    spec = Spec(**yaml.safe_load(s))
    dc = DagCompiler(spec=spec)
    assert isinstance(dc.spec.workflow[0], TaskInstance)


def test_extra_forbid_raises():
    s = dedent(
        # this workflow has an extra key, `observations` in the second task
        # this is a mistake, as this should be nested under a `partial` block
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            observations: ${{ workflow.obs.return }}
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
        (
            "get_subjectgroup_observations",
            "`get_subjectgroup_observations` is a registered known task name.",
        ),
        ("draw_ecomap", "`draw_ecomap` is a registered known task name."),
        (
            "this_id_is_more_than_32_characters_long",
            "`this_id_is_more_than_32_characters_long` is too long; max length is 32 characters.",
        ),
    ],
)
def test_invalid_id_raises(invalid_id: str, raises_match: str):
    s = dedent(
        f"""\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: {invalid_id}
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(ValidationError, match=raises_match):
        _ = Spec(**yaml.safe_load(s))


def test_ids_must_be_unique():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: obs
            task: process_relocations
        """
    )
    expected_error_text = re.escape(
        "All task instance `id`s must be unique in the workflow. Found duplicate ids: "
        "id='obs' is shared by ['Get Subjectgroup Observations', 'Process Relocations']"
    )
    with pytest.raises(ValidationError, match=expected_error_text):
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
        id: calculate_time_density
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


@pytest.mark.parametrize(
    "arg_dep_id, valid_id_of_another_task",
    [
        ("obs", True),
        ("get_subjectgroup_observations", False),
    ],
)
def test_partial_args_must_be_valid_id_of_another_task(
    arg_dep_id: str,
    valid_id_of_another_task: bool,
):
    s = dedent(
        f"""\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
                observations: ${{{{ workflow.{arg_dep_id}.return }}}}
        """
    )
    if valid_id_of_another_task:
        spec = Spec(**yaml.safe_load(s))
        assert spec.workflow[1].partial == {
            "observations": [TaskIdVariable(value="obs", suffix="return")]
        }
    else:
        with pytest.raises(
            ValidationError,
            match=re.escape(
                f"Task `Process Relocations` has an arg dependency `{arg_dep_id}` that is "
                "not a valid task id. Valid task ids for this workflow are: ['obs', 'relocs']",
            ),
        ):
            _ = Spec(**yaml.safe_load(s))


@pytest.mark.parametrize(
    "arg_dep_ids, all_valid_ids_of_another_task",
    [
        # correct because both are valid ids of another task
        (["map_widget", "plot_widget"], True),
        # incorrect because `draw_ecoplot` is not a valid id of another task, but
        # rather a known task name for another task (a subtle but important typo)
        (["map_widget", "draw_ecoplot"], False),
    ],
)
def test_all_partial_array_members_must_be_valid_id_of_another_task(
    arg_dep_ids: list[str],
    all_valid_ids_of_another_task: bool,
):
    s = dedent(
        f"""\
        id: create_dashboard
        workflow:
          - name: Create Map Widget Single View
            id: map_widget
            task: draw_ecomap
          - name: Create Plot Widget Single View
            id: plot_widget
            task: draw_ecoplot
          - name: Gather Dashboard
            id: dashboard
            task: gather_dashboard
            partial:
              widgets:
                - ${{{{ workflow.{arg_dep_ids[0]}.return }}}}
                - ${{{{ workflow.{arg_dep_ids[1]}.return }}}}
        """
    )
    if all_valid_ids_of_another_task:
        spec = Spec(**yaml.safe_load(s))
        assert spec.workflow[2].partial == {
            "widgets": [TaskIdVariable(value=v, suffix="return") for v in arg_dep_ids]
        }
    else:
        with pytest.raises(
            ValidationError,
            match=re.escape(
                f"Task `Gather Dashboard` has an arg dependency `{arg_dep_ids[1]}` that is not a "
                "valid task id. Valid task ids for this workflow are: "
                "['map_widget', 'plot_widget', 'dashboard']",
            ),
        ):
            _ = Spec(**yaml.safe_load(s))


@pytest.mark.parametrize(
    "invalid_name, raises_match",
    [
        (
            "1calc_time_density",
            "`1calc_time_density` is not a valid python identifier.",
        ),
        ("return", "`return` is a python keyword."),
        ("map", "`map` is a built-in python function."),
        (
            "this_name_is_more_than_64_characters_long_which_is_really_quite_long_indeed",
            re.escape(
                "`this_name_is_more_than_64_characters_long_which_is_really_quite_long_indeed` "
                "is too long; max length is 64 characters."
            ),
        ),
    ],
)
def test_invaild_spec_name_raises(invalid_name: str, raises_match: str):
    s = dedent(
        f"""\
        id: {invalid_name}
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(ValidationError, match=raises_match):
        _ = Spec(**yaml.safe_load(s))


def test_method_default():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
        """
    )
    spec = Spec(**yaml.safe_load(s))
    assert spec.workflow[0].method == "call"


def test_only_oneof_map_or_mapvalues():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            map:
              argnames: [a, b]
              argvalues: ${{ workflow.obs.return }}  # this is nonsense, but it's not what's being tested
            mapvalues:
              argnames: c
              argvalues: ${{ workflow.obs.return }}  # this is nonsense, but it's not what's being tested
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task `Process Relocations` cannot have both `map` and `mapvalues` set. "
            "Please choose one or the other."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_depends_on_self_in_partial_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
              observations: ${{ workflow.relocs.return }}
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task `Process Relocations` has an arg dependency that references itself: "
            "`relocs`. Task instances cannot depend on their own return values."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_depends_on_self_in_map_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            map:
              argnames: observations
              argvalues: ${{ workflow.relocs.return }}
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task `Process Relocations` has an arg dependency that references itself: "
            "`relocs`. Task instances cannot depend on their own return values."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_depends_on_self_in_mapvalues_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            mapvalues:
              argnames: observations
              argvalues: ${{ workflow.relocs.return }}
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task `Process Relocations` has an arg dependency that references itself: "
            "`relocs`. Task instances cannot depend on their own return values."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_task_id_collides_with_spec_id_raises():
    s = dedent(
        """\
        id: get_subjects
        workflow:
          - name: Get Subjectgroup Observations
            id: get_subjects
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task `id`s cannot be the same as the spec `id`. "
            "The `id` of task `Get Subjectgroup Observations` is `get_subjects`, "
            "which is the same as the spec `id`. "
            "Please choose a different `id` for this task."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_task_instance_dependencies_property():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
              observations: ${{ workflow.obs.return }}
          - name: Transform Relocations to Trajectories
            id: traj
            task: relocations_to_trajectory
            partial:
              relocations: ${{ workflow.relocs.return }}
        """
    )
    spec = Spec(**yaml.safe_load(s))
    assert spec.task_instance_dependencies == {
        "obs": [],
        "relocs": ["obs"],
        "traj": ["relocs"],
    }


def test_wrong_topological_order_partial_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
              observations: ${{ workflow.obs.return }}
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task instances are not in topological order. "
            "`Process Relocations` depends on `Get Subjectgroup Observations`, "
            "but `Get Subjectgroup Observations` is defined after `Process Relocations`."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_wrong_topological_order_map_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Process Relocations
            id: relocs
            task: process_relocations
            map:
              argnames: observations
              argvalues: ${{ workflow.obs.return }}
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task instances are not in topological order. "
            "`Process Relocations` depends on `Get Subjectgroup Observations`, "
            "but `Get Subjectgroup Observations` is defined after `Process Relocations`."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_wrong_topological_order_mapvalues_raises():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Process Relocations
            id: relocs
            task: process_relocations
            mapvalues:
              argnames: observations
              argvalues: ${{ workflow.obs.return }}
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
        """
    )
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "Task instances are not in topological order. "
            "`Process Relocations` depends on `Get Subjectgroup Observations`, "
            "but `Get Subjectgroup Observations` is defined after `Process Relocations`."
        ),
    ):
        _ = Spec(**yaml.safe_load(s))


def test_generate_dag_smoke():
    s = dedent(
        """\
        id: calculate_time_density
        workflow:
          - name: Get Subjectgroup Observations
            id: obs
            task: get_subjectgroup_observations
          - name: Process Relocations
            id: relocs
            task: process_relocations
            partial:
              observations: ${{ workflow.obs.return }}
          - name: Transform Relocations to Trajectories
            id: traj
            task: relocations_to_trajectory
            partial:
              relocations: ${{ workflow.relocs.return }}
        """
    )
    spec = Spec(**yaml.safe_load(s))
    dc = DagCompiler(spec=spec)
    dag = dc.generate_dag()
    assert isinstance(dag, str)
