import json
import shutil
import sys
from pathlib import Path
from typing import Annotated, Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from packaging.requirements import SpecifierSet
from packaging.version import Version
from pydantic import Field, BaseModel, Discriminator, Tag as PydanticTag
from pydantic.functional_validators import BeforeValidator


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


def _parse_version_or_specifier(input_str):
    if any(op in input_str for op in ["<", ">", "=", "!", "~"]):
        return SpecifierSet(input_str)
    elif input_str == "*":
        return SpecifierSet()
    else:
        return Version(input_str)


VersionOrSpecSet = Annotated[
    Version | SpecifierSet,
    BeforeValidator(_parse_version_or_specifier),
    PydanticTag("short-form-conda-dep"),
]


class LongFormCondaDependency(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    version: VersionOrSpecSet
    channel: str = "conda-forge"


def _short_versus_long_form(value: Any) -> str:
    if isinstance(value, dict):
        return "long-form-conda-dep"
    return "short-form-conda-dep"


CondaDependency = Annotated[
    VersionOrSpecSet
    | Annotated[LongFormCondaDependency, PydanticTag("long-form-conda-dep")],
    Discriminator(_short_versus_long_form),
]
FeatureName = str
PixiTaskName = str
PixiTaskCommand = str


class Feature(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    dependencies: dict[str, CondaDependency]
    tasks: dict[PixiTaskName, PixiTaskCommand]


class Environment(BaseModel):
    features: list[FeatureName] = Field(default_factory=list)
    solve_group: str = Field(default="default", alias="solve-group")


class PixiToml(BaseModel):
    """The pixi.toml file that specifies the workflow."""

    model_config = dict(arbitrary_types_allowed=True)

    project: PixiProject
    pypi_dependencies: dict[str, PypiDependency] = Field(..., alias="pypi-dependencies")
    dependencies: dict[str, CondaDependency]
    feature: dict[FeatureName, Feature]
    environments: dict[str, Environment]

    @classmethod
    def from_file(cls, path: str) -> "PixiToml":
        with open(path, "rb") as f:
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
