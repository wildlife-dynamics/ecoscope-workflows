import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest
import ruamel.yaml

from ecoscope_workflows.compiler import DagCompiler, DagTypes, Spec
from ecoscope_workflows.registry import TaskTag, known_tasks

EXAMPLES = Path(__file__).parent.parent / "examples"


def _spec_path_to_dag_fname(path: Path, dag_type: DagTypes) -> str:
    return f"{path.stem.replace('-', '_')}_dag.{dag_type.replace('-', '_')}.py"


def _spec_path_to_jsonschema_fname(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_params_fillable.json"


def _spec_path_to_yaml_fname(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_params_fillable.yaml"


def _spec_path_to_param_fname(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_params.yaml"


@dataclass
class SpecFixture:
    path: Path
    spec: dict


@pytest.fixture(
    params=[
        path.absolute() for path in EXAMPLES.joinpath("compilation-specs").iterdir()
    ],
    ids=[path.name for path in EXAMPLES.joinpath("compilation-specs").iterdir()],
)
def spec_fixture(request: pytest.FixtureRequest) -> SpecFixture:
    example_spec_path: Path = request.param
    yaml = ruamel.yaml.YAML(typ="safe")
    with open(example_spec_path) as f:
        spec_dict = yaml.load(f)
    return SpecFixture(example_spec_path, spec_dict)


@pytest.mark.parametrize(
    "dag_type",
    [
        "jupytext",
        "script-async",
        "script-sequential",
    ],
)
def test_generate_dag(spec_fixture: SpecFixture, dag_type: DagTypes):
    spec = Spec(**spec_fixture.spec)
    dag_compiler = DagCompiler(spec=spec)
    dag_str = dag_compiler.generate_dag(dag_type)
    script_fname = _spec_path_to_dag_fname(path=spec_fixture.path, dag_type=dag_type)
    with open(EXAMPLES / "dags" / script_fname) as f:
        assert dag_str == f.read()


def test_dag_params_jsonschema(spec_fixture: SpecFixture):
    spec = Spec(**spec_fixture.spec)
    dag_compiler = DagCompiler(spec=spec)
    params = dag_compiler.get_params_jsonschema()
    jsonschema_fname = _spec_path_to_jsonschema_fname(spec_fixture.path)
    with open(EXAMPLES / "params" / jsonschema_fname) as f:
        assert params == json.load(f)


def test_dag_params_fillable_yaml(spec_fixture: SpecFixture):
    spec = Spec(**spec_fixture.spec)
    dag_compiler = DagCompiler(spec=spec)
    yaml_str = dag_compiler.get_params_fillable_yaml()
    yaml = ruamel.yaml.YAML(typ="rt")
    yaml_fname = _spec_path_to_yaml_fname(spec_fixture.path)
    with open(EXAMPLES / "params" / yaml_fname) as f:
        assert yaml.load(yaml_str) == yaml.load(f)


@dataclass
class EndToEndFixture:
    spec_fixture: SpecFixture
    param_path: Path
    mock_tasks: list[str]
    assert_that_stdout: list[Callable[[str], bool]]


# TODO: package this alongside task somehow
assert_that_stdout = {
    "patrol_workflow.yaml": [
        (
            lambda out: "A dashboard for visualizing patrol trajectories, patrols events, and time density."
            in out
        ),
        lambda out: "widget_type='map', title='Trajectories & Patrol Events Map'"
        in out,
        lambda out: "widget_type='map', title='Time Density Map'" in out,
        lambda out: "widget_type='plot', title='Patrol Events Bar Chart'" in out,
        lambda out: "widget_type='plot', title='Patrol Events Pie Chart'" in out,
        lambda out: "widget_type='single_value', title='Total Patrols'" in out,
        lambda out: "widget_type='single_value', title='Total Time'" in out,
        lambda out: "widget_type='single_value', title='Total Distance'" in out,
        lambda out: "widget_type='single_value', title='Average Speed'" in out,
        lambda out: "widget_type='single_value', title='Max Speed'" in out,
    ],
    "subject_tracking.yaml": [
        lambda out: "A dashboard for visualizing subject trajectories and home range."
        in out,
        lambda out: "widget_type='map', title='Subject Group Trajectory Map'" in out,
        lambda out: "widget_type='single_value', title='Mean Speed'" in out,
        lambda out: "widget_type='single_value', title='Max Speed'," in out,
        lambda out: "widget_type='single_value', title='Number of Locations'" in out,
        lambda out: "widget_type='map', title='Home Range Map'" in out,
    ],
    "patrol_events.yaml": [
        lambda out: "A dashboard for visualizing patrol events" in out,
        lambda out: "widget_type='map', title='Patrol Events Map'" in out,
        lambda out: "widget_type='map', title='Density Map'" in out,
        lambda out: "widget_type='map', title='Grouped Patrol Events Map'" in out,
        lambda out: "widget_type='map', title='Grouped Density Map'" in out,
        lambda out: "widget_type='plot', title='Patrol Events Bar Chart'" in out,
        lambda out: "widget_type='plot', title='Patrol Events Pie Chart'" in out,
    ],
}


@pytest.fixture
def end_to_end(spec_fixture: SpecFixture) -> EndToEndFixture:
    return EndToEndFixture(
        spec_fixture=spec_fixture,
        param_path=EXAMPLES.joinpath(
            "params", _spec_path_to_param_fname(path=spec_fixture.path)
        ),
        mock_tasks=[
            task
            for task in [t["task"] for t in spec_fixture.spec["workflow"]]
            # mock tasks that require io
            # TODO: this could also be a default for the compiler in --testing mode!
            if TaskTag.io in known_tasks[task].tags
        ],
        assert_that_stdout=assert_that_stdout[spec_fixture.path.name],
    )


@pytest.mark.parametrize("dag_type", ["script-sequential", "script-async"])
def test_end_to_end(dag_type: DagTypes, end_to_end: EndToEndFixture, tmp_path: Path):
    spec = Spec(**end_to_end.spec_fixture.spec)
    dc = DagCompiler(spec=spec)
    script = dc.generate_dag(dag_type=dag_type, mock_io=True)
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    script_outpath = tmp / "script.py"
    with open(script_outpath, mode="w") as f:
        f.write(script)

    cmd = (
        f"{sys.executable} -W ignore {script_outpath.as_posix()} "
        f"--config-file {end_to_end.param_path.as_posix()}"
    )
    env = os.environ.copy()
    env["ECOSCOPE_WORKFLOWS_RESULTS"] = tmp.as_posix()
    if dag_type == "script-async" and not os.environ.get("LITHOPS_CONFIG_FILE"):
        # a lithops test is requested but no lithops config is set in the environment
        # users can set this in their environment to avoid this, to test particular
        # lithops configurations. but if they don't, we'll set a default one here.
        lithops_config_outpath = tmp / "lithops.yaml"
        lithops_config = {
            "lithops": {
                "backend": "localhost",
                "storage": "localhost",
                "log_level": "INFO",
                "data_limit": 16,
            },
            "localhost": {"runtime": sys.executable},
        }
        yaml = ruamel.yaml.YAML(typ="safe")
        with open(lithops_config_outpath, mode="w") as f:
            yaml.dump(lithops_config, f)

        env["LITHOPS_CONFIG_FILE"] = lithops_config_outpath.as_posix()

    proc = subprocess.Popen(
        cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    returncode = proc.wait()
    if returncode != 0:
        assert proc.stderr is not None
        raise ValueError(f"{cmd = } failed with:\n {proc.stderr.read()}")
    assert returncode == 0
    assert proc.stdout is not None
    stdout = proc.stdout.read().strip()
    for assert_fn in end_to_end.assert_that_stdout:
        assert assert_fn(stdout)
