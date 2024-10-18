# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "a14c0deb652592fad3edfb3b99b76dc2ed865482e7948f3915215fe3626119e9"


from pathlib import Path
from typing import get_args

import pytest
import ruamel.yaml
from fastapi.testclient import TestClient

from ecoscope_workflows_core.testing import TestCase
from ecoscope_workflows_patrol_events_workflow.app import app
from ecoscope_workflows_patrol_events_workflow.formdata import FormData


ARTIFACTS = Path(__file__).parent.parent
TEST_CASES_YAML = ARTIFACTS.parent / "test-cases.yaml"
ENTRYPOINT = "ecoscope-workflows-patrol-events-workflow"


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--case", action="store")


@pytest.fixture(scope="session")
def test_cases_yaml() -> Path:
    return Path(TEST_CASES_YAML)


@pytest.fixture(scope="session")
def case(pytestconfig: pytest.Config, test_cases_yaml: Path) -> TestCase:
    case_name = pytestconfig.getoption("case")
    yaml = ruamel.yaml.YAML(typ="safe")
    all_cases = yaml.load(test_cases_yaml.read_text())
    assert case_name in all_cases, f"{case_name =} not found in {test_cases_yaml =}"
    return TestCase(**all_cases[case_name])


@pytest.fixture(scope="session")
def formdata(case: TestCase) -> dict:
    """From a flat set of paramaters, create nested representation to reflect how the RJSF
    formdata would be structured. This is used for testing the formdata validation endpoint,
    and allows us to test the formdata validation endpoint without having to manually create
    the nested structure.
    """
    formdata: dict[str, dict] = {}
    aliased_annotations = {
        v.alias: v.annotation for v in FormData.model_fields.values() if v.alias
    }
    task_groups = {
        k: list(get_args(v)[0].model_fields) for k, v in aliased_annotations.items()
    }
    for k, v in case.params.items():
        if k in FormData.model_fields:
            formdata[k] = v
        else:
            group = next(g for g in task_groups if k in task_groups[g])
            if group in formdata:
                formdata[group].update({k: v})
            else:
                formdata[group] = {k: v}
    return formdata


@pytest.fixture(params=["async", "sequential"])
def execution_mode(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=[True], ids=["mock-io"])
def mock_io(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(scope="session")
def entrypoint() -> str:
    return ENTRYPOINT


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
