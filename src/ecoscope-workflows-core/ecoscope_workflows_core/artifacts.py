import json
import shutil
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from pydantic import BaseModel, Field

from ecoscope_workflows_core._models import _AllowArbitraryTypes
from ecoscope_workflows_core.requirements import (
    ChannelType,
    NamelessMatchSpecType,
    PlatformType,
    CHANNELS,
    PLATFORMS,
)


class Dags(BaseModel):
    """Target directory for the generated DAGs."""

    jupytext: str = Field(..., alias="jupytext.py")
    script_async_mock_io: str = Field(..., alias="script-async.mock-io.py")
    script_async: str = Field(..., alias="script-async.py")
    script_sequential_mock_io: str = Field(..., alias="script-sequential.mock-io.py")
    script_sequential: str = Field(..., alias="script-sequential.py")


class PixiProject(_AllowArbitraryTypes):
    name: str
    # mypy throws:
    # `error: List comprehension has incompatible type List[str | None]; expected List[Channel]  [misc]`
    # `error: List comprehension has incompatible type List[str]; expected List[Platform]  [misc]`
    # but pydantic parsing handles these correctly (and stumbles without the list comprehension)
    channels: list[ChannelType] = [c.name for c in CHANNELS]  # type: ignore[misc]
    platforms: list[PlatformType] = [str(p) for p in PLATFORMS]  # type: ignore[misc]


FeatureName = str
PixiTaskName = str
PixiTaskCommand = str


class Feature(_AllowArbitraryTypes):
    """A `pixi.toml` feature definition."""

    dependencies: dict[str, NamelessMatchSpecType]
    tasks: dict[PixiTaskName, PixiTaskCommand] = Field(default_factory=dict)


class Environment(BaseModel):
    features: list[FeatureName] = Field(default_factory=list)
    solve_group: str = Field(default="default", alias="solve-group")


class PixiToml(_AllowArbitraryTypes):
    """The pixi.toml file that specifies the workflow."""

    project: PixiProject
    dependencies: dict[str, NamelessMatchSpecType]
    feature: dict[FeatureName, Feature] = Field(default_factory=dict)
    environments: dict[str, Environment] = Field(default_factory=dict)

    @classmethod
    def from_file(cls, src: str | Path) -> "PixiToml":
        if isinstance(src, str):
            src = Path(src)
        with src.open("rb") as f:
            content = tomllib.load(f)
        return cls(**content)

    @classmethod
    def from_text(cls, text: str) -> "PixiToml":
        return cls(**tomllib.loads(text))

    def dump(self, dst: Path):
        with dst.open("wb") as f:
            tomli_w.dump(self.model_dump(), f)


CONFTEST = """\
import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption("--case", action="store")


@pytest.fixture(scope="session")
def case(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("case")
"""

TEST_DAGS = """\
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
"""


class Tests(BaseModel):
    conftest: str = Field(default=CONFTEST, alias="conftest.py")
    test_dags: str = Field(default=TEST_DAGS, alias="test_dags.py")


DEFAULT_PIXI_TOML = """\
[project]
name = "default"
channels = [
    "ecoscope-workflows-local",
    "ecoscope-workflows-release",
    "conda-forge",
]
platforms = ["linux-64", "linux-aarch64", "osx-arm64"]

[dependencies]
ecoscope-workflows-core = { version = "*", channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }
ecoscope-workflows-ext-ecoscope = {version = "*", channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }

[feature.test.dependencies]
pytest = "*"
[feature.test.tasks]
test-async-local-mock-io = "python -m pytest tests -k 'async and mock-io'"
test-sequential-local-mock-io = "python -m pytest tests -k 'sequential and mock-io'"

[environments]
default = { solve-group = "default" }
test = { features = ["test"], solve-group = "default" }

"""
# todo: support build; push; deploy; run; test; etc. tasks
# [feature.docker.tasks]
# build-base = "docker build -t mode-map-base -f Dockerfile.base ."
# build-runner = "docker build -t mode-map-runner -f Dockerfile.runner ."
# build-deploy-worker = "docker build -t mode-map-worker -f Dockerfile.worker ."


def _default_pixi_toml():
    return PixiToml.from_text(DEFAULT_PIXI_TOML)


class WorkflowArtifacts(_AllowArbitraryTypes):
    dags: Dags
    params_jsonschema: dict
    pixi_toml: PixiToml = Field(default_factory=_default_pixi_toml)
    tests: Tests = Field(default_factory=Tests)

    def dump(self, root: Path, clobber: bool = False):
        if root.exists() and not clobber:
            raise FileExistsError(
                f"Path '{root}' already exists. Set clobber=True to overwrite."
            )
        if root.exists() and clobber and not root.is_dir():
            raise FileExistsError(f"Cannot clobber existing '{root}'; not a directory.")
        if root.exists() and clobber:
            shutil.rmtree(root)
        root.joinpath("dags").mkdir(parents=True)
        for fname, content in self.dags.model_dump(by_alias=True).items():
            root.joinpath("dags").joinpath(fname).write_text(content)

        root.joinpath("tests").mkdir(parents=True)
        for fname, content in self.tests.model_dump(by_alias=True).items():
            root.joinpath("tests").joinpath(fname).write_text(content)

        with root.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.params_jsonschema, f, indent=2)

        self.pixi_toml.dump(root.joinpath("pixi.toml"))
