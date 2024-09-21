import json
from dataclasses import dataclass
from pathlib import Path

import pytest
import ruamel.yaml

from ecoscope_workflows.compiler import DagCompiler, DagTypes, Spec

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
