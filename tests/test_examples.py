import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

import pytest
import ruamel.yaml

from ecoscope_workflows.compiler import DagCompiler, Spec
from ecoscope_workflows.registry import TaskTag, known_tasks

EXAMPLES = Path(__file__).parent.parent / "examples"

TemplateName = Literal[
    "script-async.jinja2", "script-sequential.jinja2", "jupytext.jinja2"
]


def _spec_path_to_dag_fname(path: Path, template: TemplateName) -> str:
    return (
        f"{path.stem.replace('-', '_')}_dag.{Path(template).stem.replace('-', '_')}.py"
    )


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
    "template",
    [
        "jupytext.jinja2",
        "script-async.jinja2",
        "script-sequential.jinja2",
    ],
)
def test_generate_dag(spec_fixture: SpecFixture, template: TemplateName):
    spec = Spec(**spec_fixture.spec)
    dag_compiler = DagCompiler(spec=spec)
    dag_compiler.template = template
    dag_str = dag_compiler.generate_dag()
    script_fname = _spec_path_to_dag_fname(path=spec_fixture.path, template=template)
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
    "mode-map.yaml": [
        lambda out: ".html" in out,
    ],
    "mode-mapvalues.yaml": [
        lambda out: "A dashboard demonstrating grouped data." in out,
        lambda out: "GroupedWidget(widget_type='map', title='Grouped Ecomaps'" in out,
        lambda out: (
            "grouper_choices={Grouper(index_name='event_type', display_name='Event Type', "
            "help_text='The type of event that occurred.'): ['fence_rep', 'fire_rep', 'radio_rep', "
            "'rainfall_rep', 'traffic_rep', 'wildlife_sighting_rep']}"
        )
        in out,
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


@pytest.mark.parametrize(
    "template", ["script-sequential.jinja2", "script-async.jinja2"]
)
def test_end_to_end(template: str, end_to_end: EndToEndFixture, tmp_path: Path):
    spec = Spec(**end_to_end.spec_fixture.spec)
    dc = DagCompiler(spec=spec)
    dc.template = template
    dc.testing = True
    dc.mock_tasks = end_to_end.mock_tasks
    script = dc.generate_dag()
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    script_outpath = tmp / "script.py"
    with open(script_outpath, mode="w") as f:
        f.write(script)

    if (
        python_exe := os.environ.get("ECOSCOPE_WORKFLOWS_TESTING_PYTHON_EXECUTABLE")
    ) is None:
        # if not explicitly set, use the current python executable, assuming we're not in
        # mamba environment, in which case we need to use the mamba executable to run the script
        # since python may not be available in PATH. the safest option is just to explicitly set
        # the python executable to use for testing on the env, but this is a reasonable default.
        python_exe = (
            # workaround for https://github.com/mamba-org/mamba/issues/2577
            f"{os.environ['MAMBA_EXE']} run -n {os.environ['CONDA_ENV_NAME']} python"
            if "mamba" in sys.executable
            else sys.executable
        )
    python_cmd = (
        f"{python_exe} -W ignore {script_outpath.as_posix()} "
        f"--config-file {end_to_end.param_path.as_posix()}"
    )
    shell = (
        os.environ.get("ECOSCOPE_WORKFLOWS_TESTING_SHELL", "")
        .replace('"', "")
        .replace("'", "")
    )
    cmd = f"{shell} -c '{python_cmd}'" if shell else python_cmd
    env = os.environ.copy()
    env["ECOSCOPE_WORKFLOWS_RESULTS"] = tmp.as_posix()
    if template == "script-async.jinja2":
        lithops_config_outpath = tmp / "lithops.yaml"
        lithops_config = {
            "lithops": {
                "backend": "localhost",
                "storage": "localhost",
                "log_level": "INFO",
                "data_limit": 16,
            }
        }
        yaml = ruamel.yaml.YAML(typ="safe")
        with open(lithops_config_outpath, mode="w") as f:
            yaml.dump(lithops_config, f)

        env["LITHOPS_CONFIG_FILE"] = lithops_config_outpath.as_posix()

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        shell=(True if shell else False),
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
