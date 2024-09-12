from pathlib import Path

import pytest

from ecoscope_workflows.testing import test_case


BLD = Path(__file__).parent.parent
WORKFLOWS = [
    p
    for p in BLD.joinpath("workflows").iterdir()
    if p.suffix == ".py" and not p.name.startswith("_")
]
TEST_CASES_YAML = BLD.parent / "test-cases.yaml"


@pytest.mark.parametrize("script", WORKFLOWS, ids=[p.stem for p in WORKFLOWS])
def test_end_to_end(script: Path, case: str, tmp_path: Path):
    print(f"Running end-to-end test for {script =} with {case =}:")
    test_case(script, case, TEST_CASES_YAML, tmp_path)
    print("Success!")
