# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "7f7a2953093d602c7a7746ca4822e4f6c3498150d973f09f090ad62a8b580361"


from pathlib import Path

import pytest
import ruamel.yaml
from fastapi.testclient import TestClient

from ecoscope_workflows_core.testing import TestCase
from ecoscope_workflows_mode_mapvalues_workflow.app import app


ARTIFACTS = Path(__file__).parent.parent
TEST_CASES_YAML = ARTIFACTS.parent / "test-cases.yaml"
ENTRYPOINT = "ecoscope-workflows-mode-mapvalues-workflow"


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
