# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "a45a987fc5f35a6d3f9e1ac858aa050ef6afeca2bb96c8deda154a804dc69253"


from pathlib import Path

from ecoscope_workflows_core.testing import TestCase, run_cli_test_case


def test_cli(
    entrypoint: str,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    run_cli_test_case(entrypoint, execution_mode, mock_io, case, tmp_path)
