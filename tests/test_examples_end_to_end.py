import subprocess
from pathlib import Path

import pytest
import yaml

from ecoscope_workflows.compiler import DagCompiler

EXAMPLE_SPECS_DIR = Path(__file__).parent.parent / "examples" / "compilation-specs"


@pytest.fixture(
    params=[path.absolute() for path in EXAMPLE_SPECS_DIR.iterdir()],
    ids=[path.name for path in EXAMPLE_SPECS_DIR.iterdir()],
)
def spec(request: pytest.FixtureRequest) -> dict:
    example_spec_path = request.param
    with open(example_spec_path) as f:
        return yaml.safe_load(f)


def test_example(spec: dict, tmp_path: Path):
    dc = DagCompiler.from_spec(spec=spec)
    dc.template = "script-sequential.jinja2"
    script = dc._generate_dag()
    tmp_dir = tmp_path / "scripts"
    tmp_dir.mkdir()
    outpath = tmp_dir / "script.py"
    with open(outpath, mode="w") as f:
        f.write(script)
    
    cmd = ["python3", outpath.as_posix(), "--help"]
    out = subprocess.run(cmd)
    print(out.stdout)
