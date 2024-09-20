from pathlib import Path

import pytest

from ecoscope_workflows_core.testing import test_case


WORKFLOW = Path(__file__).parent.parent
DAGS = [
    p
    for p in WORKFLOW.joinpath("dags").iterdir()
    if p.suffix == ".py" and not p.name.startswith("_")
]
TEST_CASES_YAML = WORKFLOW.parent / "test-cases.yaml"


@pytest.mark.parametrize("script", DAGS, ids=[p.stem for p in DAGS])
def test_end_to_end(script: Path, case: str, tmp_path: Path):
    test_case(script, case, TEST_CASES_YAML, tmp_path)
