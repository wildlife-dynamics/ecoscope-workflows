import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from pydantic import BaseModel, Field

from ecoscope_workflows_core._models import (
    _AllowArbitraryTypes,
    _AllowArbitraryAndValidateAssignment,
)
from ecoscope_workflows_core.requirements import (
    ChannelType,
    NamelessMatchSpecType,
    PlatformType,
    CHANNELS,
    PLATFORMS,
)


class Dags(BaseModel):
    """Target directory for the generated DAGs."""

    init_dot_py: str = Field(
        default=dedent(
            # FIXME: add import other scripts as well
            """\
            from .sequential_mock_io import main as sequential_mock_io

            __all__ = ["sequential_mock_io"]
            """
        ),
        alias="__init__.py",
    )
    jupytext: str = Field(..., alias="jupytext.py")
    script_async_mock_io: str = Field(..., alias="script-async.mock-io.py")
    script_async: str = Field(..., alias="script-async.py")
    script_sequential_mock_io: str = Field(..., alias="sequential_mock_io.py")
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


class PixiToml(_AllowArbitraryAndValidateAssignment):
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

    def add_dependency(
        self, name: str, version: str, channel: str | None = None
    ) -> None:
        """Add a dependency to the `dependencies` section."""
        deps_copy = copy.deepcopy(self.model_dump()["dependencies"])
        deps_copy[name] = {"version": version} | (
            {"channel": channel} if channel else {}
        )
        # we do not get assignment validation/parsing
        # unless we re-assign .dependencies, so do that
        self.dependencies = deps_copy

    def dump(self, dst: Path):
        with dst.open("wb") as f:
            tomli_w.dump(self.model_dump(by_alias=True), f)


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


ARTIFACTS = Path(__file__).parent.parent
TEST_CASES_YAML = ARTIFACTS.parent / "test-cases.yaml"
ENTRYPOINT = "ecoscope-workflows-mode-map-workflow"


@pytest.mark.parametrize("execution_mode", ["sequential"])
@pytest.mark.parametrize("mock_io", [True], ids=["mock-io"])
def test_end_to_end(execution_mode: str, mock_io: bool, case: str, tmp_path: Path):
    test_case(ENTRYPOINT, execution_mode, mock_io, case, TEST_CASES_YAML, tmp_path)
"""


class Tests(BaseModel):
    conftest: str = Field(default=CONFTEST, alias="conftest.py")
    test_dags: str = Field(default=TEST_DAGS, alias="test_dags.py")


MAIN_DOT_PY = """\
from io import TextIOWrapper

import click
import ruamel.yaml

from .dags import sequential_mock_io


@click.command()
@click.option(
    "--config-file",
    type=click.File("r"),
    required=True,
    help="Configuration parameters for running the workflow.",
)
@click.option(
    "--execution-mode",
    required=True,
    type=click.Choice(["async", "sequential"]),
)
@click.option(
    "--mock-io/--no-mock-io",
    is_flag=True,
    default=False,
    help="Whether or not to mock io with 3rd party services; for testing only.",
)
def main(
    config_file: TextIOWrapper,
    execution_mode: str,
    mock_io: bool,
) -> None:
    yaml = ruamel.yaml.YAML(typ="safe")
    params = yaml.load(config_file)
    match execution_mode, mock_io:
        case ("async", True):
            raise NotImplementedError
        case ("async", False):
            raise NotImplementedError
        case ("sequential", True):
            result = sequential_mock_io(params=params)
        case ("sequential", False):
            raise NotImplementedError
        case _:
            raise ValueError(f"Invalid execution mode: {execution_mode}")

    print(result)


if __name__ == "__main__":
    main()
"""


class PackageDirectory(BaseModel):
    dags: Dags
    params_jsonschema: dict
    main: str = Field(default=MAIN_DOT_PY, alias="main.py")
    init_dot_py: str = Field(default="", alias="__init__.py")


class WorkflowArtifacts(_AllowArbitraryTypes):
    release_name: str
    package_name: str
    pixi_toml: PixiToml
    pyproject_toml: str
    package: PackageDirectory
    tests: Tests = Field(default_factory=Tests)

    def lock(self):
        subprocess.run(
            f"pixi install -a --manifest-path {self.release_name}/pixi.toml".split()
        )

    def dump(self, clobber: bool = False):
        root = Path().cwd().joinpath(self.release_name)
        if root.exists() and not clobber:
            raise FileExistsError(
                f"Path '{root}' already exists. Set clobber=True to overwrite."
            )
        if root.exists() and clobber and not root.is_dir():
            raise FileExistsError(f"Cannot clobber existing '{root}'; not a directory.")
        if root.exists() and clobber:
            shutil.rmtree(root)

        root.mkdir(parents=True)

        # root artifacts
        self.pixi_toml.dump(root.joinpath("pixi.toml"))
        root.joinpath("pyproject.toml").write_text(self.pyproject_toml)
        root.joinpath("tests").mkdir(parents=True)
        for fname, content in self.tests.model_dump(by_alias=True).items():
            root.joinpath("tests").joinpath(fname).write_text(content)

        # package artifacts
        pkg = root.joinpath(self.package_name)
        pkg.mkdir(parents=True)
        pkg.joinpath("dags").mkdir(parents=True)
        # top level
        pkg.joinpath("__init__.py").write_text("")
        pkg.joinpath("main.py").write_text(self.package.main)
        with pkg.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.package.params_jsonschema, f, indent=2)
        # dags
        for fname, content in self.package.dags.model_dump(by_alias=True).items():
            pkg.joinpath("dags").joinpath(fname).write_text(content)
