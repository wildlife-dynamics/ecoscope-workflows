from pathlib import Path

import pytest

from ecoscope_workflows_core.testing import test_case


ARTIFACTS = Path(__file__).parent.parent
TEST_CASES_YAML = ARTIFACTS.parent / "test-cases.yaml"
ENTRYPOINT = "ecoscope-workflows-subject-tracking-workflow"


@pytest.mark.parametrize("execution_mode", ["async", "sequential"])
@pytest.mark.parametrize("mock_io", [True], ids=["mock-io"])
def test_end_to_end(execution_mode: str, mock_io: bool, case: str, tmp_path: Path):
    test_case(ENTRYPOINT, execution_mode, mock_io, case, TEST_CASES_YAML, tmp_path)
