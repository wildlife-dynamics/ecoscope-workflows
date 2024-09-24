import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from textwrap import dedent

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
import datamodel_code_generator as dcg
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
            """\
            from .run_async import main as run_async
            from .run_async_mock_io import main as run_async_mock_io
            from .run_sequential import main as run_sequential
            from .run_sequential_mock_io import main as run_sequential_mock_io

            __all__ = [
                "run_async",
                "run_async_mock_io",
                "run_sequential",
                "run_sequential_mock_io",
            ]
            """
        ),
        alias="__init__.py",
    )
    jupytext: str = Field(..., alias="jupytext.py")
    run_async_mock_io: str = Field(..., alias="run_async_mock_io.py")
    run_async: str = Field(..., alias="run_async.py")
    run_sequential_mock_io: str = Field(..., alias="run_sequential_mock_io.py")
    run_sequential: str = Field(..., alias="run_sequential.py")


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
    pypi_dependencies: dict[str, dict] = Field(
        default_factory=dict, alias="pypi-dependencies"
    )

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


class Tests(BaseModel):
    test_dags: str = Field(..., alias="test_dags.py")
    conftest: str = Field(default=CONFTEST, alias="conftest.py")


MAIN_DOT_PY = """\
from io import TextIOWrapper

import click
import ruamel.yaml

from .dags import (
    run_async,
    run_async_mock_io,
    run_sequential,
    run_sequential_mock_io,
)
from .params import Params


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
    params = Params(**yaml.load(config_file))
    match execution_mode, mock_io:
        case ("async", True):
            result = run_async_mock_io(params=params)
        case ("async", False):
            result = run_async(params=params)
        case ("sequential", True):
            result = run_sequential_mock_io(params=params)
        case ("sequential", False):
            result = run_sequential(params=params)
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

    def generate_params_model(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
            output = Path(tmp.name)
            dcg.generate(
                json.dumps(self.params_jsonschema),
                input_file_type=dcg.InputFileType.JsonSchema,
                input_filename="params-jsonschema.json",
                output=output,
                output_model_type=dcg.DataModelType.PydanticV2BaseModel,
            )
            model: str = output.read_text()
        return model


class WorkflowArtifacts(_AllowArbitraryTypes):
    release_name: str
    package_name: str
    pixi_toml: PixiToml
    pyproject_toml: str
    package: PackageDirectory
    tests: Tests

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
        params_model = self.package.generate_params_model()
        pkg.joinpath("params.py").write_text(params_model)
        with pkg.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.package.params_jsonschema, f, indent=2)
        # dags
        for fname, content in self.package.dags.model_dump(by_alias=True).items():
            pkg.joinpath("dags").joinpath(fname).write_text(content)
