import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

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

    init_dot_py: str = Field(..., alias="__init__.py")
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


class Tests(BaseModel):
    conftest: str = Field(..., alias="conftest.py")
    test_app: str = Field(..., alias="test_app.py")
    test_cli: str = Field(..., alias="test_cli.py")

    def dump(self, dst: Path):
        dst.joinpath("tests").mkdir(parents=True)
        for fname, content in self.model_dump(by_alias=True).items():
            dst.joinpath("tests").joinpath(fname).write_text(content)


class PackageDirectory(BaseModel):
    dags: Dags
    params_jsonschema: dict = Field(..., alias="params-jsonschema.json")
    params_model: str = Field(..., alias="params.py")
    app: str = Field(..., alias="app.py")
    cli: str = Field(..., alias="cli.py")
    dispatch: str = Field(..., alias="dispatch.py")
    init_dot_py: str = Field(default="", alias="__init__.py")

    def dump(self, dst: Path):
        for fname, content in self.model_dump(
            by_alias=True, exclude={"params_jsonschema", "dags"}
        ).items():
            dst.joinpath(fname).write_text(content)
        with dst.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.params_jsonschema, f, indent=2)
            f.write("\n")
        dst.joinpath("dags").mkdir(parents=True)
        for fname, content in self.dags.model_dump(by_alias=True).items():
            dst.joinpath("dags").joinpath(fname).write_text(content)


class WorkflowArtifacts(_AllowArbitraryTypes):
    spec_relpath: str
    release_name: str
    package_name: str
    package: PackageDirectory
    tests: Tests
    pixi_toml: PixiToml = Field(..., alias="pixi.toml")
    pyproject_toml: str = Field(..., alias="pyproject.toml")
    dockerfile: str = Field(..., alias="Dockerfile")
    dockerignore: str = Field(..., alias=".dockerignore")
    # graph_png: bytes = Field(..., alias="graph.png")
    # readme_md: str = Field(..., alias="README.md")

    @property
    def release_dir(self) -> Path:
        return (
            Path().cwd().joinpath(self.spec_relpath).parent.joinpath(self.release_name)
        )

    def lock(self):
        subprocess.run(
            f"pixi install -a --manifest-path {self.release_dir.joinpath('pixi.toml')}".split()
        )

    def dump(self, clobber: bool = False, carryover_lockfile: bool = False):
        """Dump the artifacts to disk.

        Args:
            clobber (bool, optional): Whether or not to clobber an existing build directory. Defaults to False.
            carryover_lockfile (bool, optional): In the case of combining the options `--clobber` + `--no-lock`,
                whether or not to carryover the lockfile from the clobbered directory. If true, this option
                allows for rebuilding the package with a (potentially!) functional lockfile, without paying
                the cost of actually re-locking the package. Defaults to False.
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
            if carryover_lockfile:
                lockfile = self.release_dir.joinpath("pixi.lock")
                if not lockfile.exists():
                    raise FileNotFoundError(
                        f"Cannot carryover lockfile; '{lockfile}' does not exist."
                    )
                original_lockfile = lockfile.read_text()
            shutil.rmtree(self.release_dir)

        self.release_dir.mkdir(parents=True)

        # root artifacts
        self.pixi_toml.dump(self.release_dir.joinpath("pixi.toml"))
        if carryover_lockfile:
            self.release_dir.joinpath("pixi.lock").write_text(original_lockfile)
        for k, v in {
            "pyproject.toml": self.pyproject_toml,
            "Dockerfile": self.dockerfile,
            ".dockerignore": self.dockerignore,
        }.items():
            self.release_dir.joinpath(k).write_text(v)
        # tests
        self.tests.dump(self.release_dir)
        # package artifacts
        pkg = self.release_dir.joinpath(self.package_name)
        pkg.mkdir(parents=True)
        self.package.dump(pkg)
