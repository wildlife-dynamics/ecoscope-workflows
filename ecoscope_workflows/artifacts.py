import json
import shutil
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from packaging.requirements import SpecifierSet
from packaging.version import Version
from pydantic import Field, BaseModel

CHANNELS = ["https://prefix.dev/ecoscope-workflows", "conda-forge"]
PLATFORMS = ["linux-64", "linux-aarch64", "osx-arm64"]


class Dags(BaseModel):
    """Target directory for the generated DAGs."""

    jupytext: str = Field(..., alias="jupytext.py")
    script_async_mock_io: str = Field(..., alias="script-async.mock-io.py")
    script_async: str = Field(..., alias="script-async.py")
    script_sequential_mock_io: str = Field(..., alias="script-sequential.mock-io.py")
    script_sequential: str = Field(..., alias="script-sequential.py")


class SymlinkVendor:
    pass


class PixiProject(BaseModel):
    name: str
    channels: list[str] = CHANNELS
    platforms: list[str] = PLATFORMS


class PypiDependency(BaseModel):
    path: str
    editable: bool = True


class LongFormCondaDependency(BaseModel):
    version: Version | SpecifierSet
    channel: str = "conda-forge"


FeatureName = str


class Feature(BaseModel):
    dependencies: list[dict[str, LongFormCondaDependency]]
    tasks: list[dict[str, str]]


class Environment(BaseModel):
    features: list[FeatureName]
    solve_group: str = Field(default="default", alias="solve-group")


class PixiToml(BaseModel):
    """The pixi.toml file that specifies the workflow."""

    project: PixiProject
    pypi_dependencies: list[dict[str, PypiDependency]]
    dependencies: list[dict[str, LongFormCondaDependency]]
    feature: dict[FeatureName, Feature]
    environments: dict[str, Environment]

    @classmethod
    def from_file(cls, path: str) -> "PixiToml":
        with open(path) as f:
            content = tomllib.load(f)
        return cls(**content)

    def dump(self, path: Path):
        with path.open("w") as f:
            tomli_w.dump(self.model_dump(), f)


class WorkflowArtifacts(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    dags: Dags
    # src: SymlinkVendor | None = None
    # test: ...
    params_jsonschema: dict
    # pixi_toml: dict  # if SymlinkVendor is None, we can simplify this and just install a release of workflows from prefix.dev

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

        with root.joinpath("params-jsonschema.json").open("w") as f:
            json.dump(self.params_jsonschema, f, indent=2)

        # self.pixi_toml.dump(path / "pixi.toml")
