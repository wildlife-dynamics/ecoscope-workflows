from pathlib import Path

import pytest

from ecoscope_workflows_core.testing import TestCase, run_cli_test_case


@pytest.mark.xfail(
    reason="Params parsing behavior is broken; try using click.testing.CliRunner"
)
def test_cli(
    entrypoint: str,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    run_cli_test_case(entrypoint, execution_mode, mock_io, case, tmp_path)