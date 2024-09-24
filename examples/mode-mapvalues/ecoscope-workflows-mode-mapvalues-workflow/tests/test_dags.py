from pathlib import Path

import pytest

from ecoscope_workflows_core.testing import TestCase, test_case


@pytest.mark.parametrize("execution_mode", ["async", "sequential"])
@pytest.mark.parametrize("mock_io", [True], ids=["mock-io"])
def test_end_to_end(
    entrypoint: str,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    test_case(entrypoint, execution_mode, mock_io, case, tmp_path)
