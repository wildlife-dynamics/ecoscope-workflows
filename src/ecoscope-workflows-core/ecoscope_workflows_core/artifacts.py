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
    tasks: dict[PixiTaskName, PixiTaskCommand] = Field(default_factory=dict)
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


TEST_APP = """\
from pathlib import Path

from fastapi.testclient import TestClient

from ecoscope_workflows_core.testing import TestCase


def test_app(
    client: TestClient,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    request = {"params": case.params}
    query_params = {
        "execution_mode": execution_mode,
        "mock_io": mock_io,
        "results_url": tmp_path.as_uri(),
    }
    headers = {"Content-Type": "application/json"}
    response = client.post(
        "/",
        json=request,
        params=query_params,
        headers=headers,
    )
    assert response.status_code == 200
"""


TEST_CLI = """\
from pathlib import Path

import pytest

from ecoscope_workflows_core.testing import TestCase, run_cli_test_case


@pytest.mark.xfail(reason="Params parsing behavior is broken; try using click.testing.CliRunner")
def test_cli(
    entrypoint: str,
    execution_mode: str,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    run_cli_test_case(entrypoint, execution_mode, mock_io, case, tmp_path)
"""


class Tests(BaseModel):
    conftest: str = Field(..., alias="conftest.py")
    test_app: str = Field(default=TEST_APP, alias="test_app.py")
    test_cli: str = Field(default=TEST_CLI, alias="test_cli.py")


APP = """\
import os
import tempfile
from typing import Literal

import ruamel.yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, SecretStr

from .dispatch import dispatch
from .params import Params


app = FastAPI(
    title="Ecoscope Workflows Runner",
    debug=True,
    version="0.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to only the fastapi server, anywhere else?
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


class Lithops(BaseModel):
    backend: str = "gcp_cloudrun"
    storage: str = "gcp_storage"
    log_level: str = "DEBUG"
    data_limit: int = 16


class GCP(BaseModel):
    region: str = "us-central1"
    credentials_path: str = (
        "placeholder"  # os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )


class GCPCloudRun(BaseModel):
    runtime: str = "placeholder"  # os.environ["LITHOPS_GCP_CLOUDRUN_RUNTIME"]
    runtime_cpu: int = 2
    runtime_memory: int = 1000


class LithopsConfig(BaseModel):
    lithops: Lithops = Field(default_factory=Lithops)
    gcp: GCP = Field(default_factory=GCP)
    gcp_cloudrun: GCPCloudRun = Field(default_factory=GCPCloudRun)


@app.post("/", status_code=200)
def run(
    params: Params,
    execution_mode: Literal["async", "sequential"],
    mock_io: bool,
    results_url: str,
    data_connections_env_vars: dict[str, SecretStr] | None = None,
    lithops_config: LithopsConfig | None = None,
    callback_url: str | None = None,  # TODO: authentication (hmac)
):
    yaml = ruamel.yaml.YAML(typ="safe")
    update_env = {"ECOSCOPE_WORKFLOWS_RESULTS": results_url}

    if execution_mode == "async":
        if not lithops_config:
            lithops_config = LithopsConfig()
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".yaml"
        ) as lithops_config_file:
            yaml.dump(lithops_config.model_dump(), lithops_config_file)
            update_env["LITHOPS_CONFIG_FILE"] = lithops_config_file.name

    if data_connections_env_vars:
        update_env |= {
            k: v.get_secret_value() for k, v in data_connections_env_vars.items()
        }
    os.environ.update(update_env)
    try:
        result = dispatch(execution_mode, mock_io, params)
        if callback_url:
            raise NotImplementedError("Callbacks are not yet implemented.")
    except Exception as e:
        return {"error": str(e)}
    finally:
        for k in update_env:
            del os.environ[k]

    return result
"""

CLI = """\
from io import TextIOWrapper

import click
import ruamel.yaml

from .dispatch import dispatch
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

    result = dispatch(execution_mode, mock_io, params)

    print(result)


if __name__ == "__main__":
    main()
"""

DISPATCH = """\
from typing import Any

from .dags import (
    run_async,
    run_async_mock_io,
    run_sequential,
    run_sequential_mock_io,
)
from .params import Params


def dispatch(
    execution_mode: str,  # TODO: literal type
    mock_io: bool,
    params: Params,
) -> Any:  # TODO: Dynamically define the return type
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

    return result

"""


class PackageDirectory(BaseModel):
    dags: Dags
    params_jsonschema: dict
    app: str = Field(default=APP, alias="app.py")
    cli: str = Field(default=CLI, alias="cli.py")
    dispatch: str = Field(default=DISPATCH, alias="dispatch.py")
    init_dot_py: str = Field(default="", alias="__init__.py")

    def generate_params_model(self) -> str:
        with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
            output = Path(tmp.name)
            dcg.generate(
                json.dumps(self.params_jsonschema),
                input_file_type=dcg.InputFileType.JsonSchema,
                input_filename="params-jsonschema.json",
                output=output,
                output_model_type=dcg.DataModelType.PydanticV2BaseModel,
                use_subclass_enum=True,
            )
            model: str = output.read_text()
        return model


DOCKERIGNORE = """\
.pixi/
*.egg-info/
"""


class WorkflowArtifacts(_AllowArbitraryTypes):
    spec_relpath: str
    release_name: str
    package_name: str
    pixi_toml: PixiToml
    pyproject_toml: str
    package: PackageDirectory
    tests: Tests
    dockerfile: str
    dockerignore: str = Field(default=DOCKERIGNORE, alias=".dockerignore")

    @property
    def release_dir(self) -> Path:
        return (
            Path().cwd().joinpath(self.spec_relpath).parent.joinpath(self.release_name)
        )

    def lock(self):
        subprocess.run(
            f"pixi install -a --manifest-path {self.release_dir.joinpath('pixi.toml')}".split()
        )

    def dump(self, clobber: bool = False):
        """Dump the artifacts to disk.

        Args:
            clobber (bool, optional): Whether or not to clobber an existing build directory. Defaults to False.
        """
        if self.release_dir.exists() and not clobber:
            raise FileExistsError(
                f"Path '{self.release_dir}' already exists. Set clobber=True to overwrite."
            )
        if self.release_dir.exists() and clobber and not self.release_dir.is_dir():
            raise FileExistsError(
                f"Cannot clobber existing '{self.release_dir}'; not a directory."
            )
        if self.release_dir.exists() and clobber:
            shutil.rmtree(self.release_dir)

        self.release_dir.mkdir(parents=True)

        # root artifacts
        self.pixi_toml.dump(self.release_dir.joinpath("pixi.toml"))
        self.release_dir.joinpath("pyproject.toml").write_text(self.pyproject_toml)
        self.release_dir.joinpath("Dockerfile").write_text(self.dockerfile)
        self.release_dir.joinpath(".dockerignore").write_text(self.dockerignore)
        self.release_dir.joinpath("tests").mkdir(parents=True)
        for fname, content in self.tests.model_dump(by_alias=True).items():
            self.release_dir.joinpath("tests").joinpath(fname).write_text(content)

        # package artifacts
        pkg = self.release_dir.joinpath(self.package_name)
        pkg.mkdir(parents=True)
        pkg.joinpath("dags").mkdir(parents=True)
        # top level
        pkg.joinpath("__init__.py").write_text("")
        pkg.joinpath("app.py").write_text(self.package.app)
        pkg.joinpath("cli.py").write_text(self.package.cli)
        pkg.joinpath("dispatch.py").write_text(self.package.dispatch)
        params_model = self.package.generate_params_model()
        pkg.joinpath("params.py").write_text(params_model)
        with pkg.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.package.params_jsonschema, f, indent=2)
        # dags
        for fname, content in self.package.dags.model_dump(by_alias=True).items():
            pkg.joinpath("dags").joinpath(fname).write_text(content)
