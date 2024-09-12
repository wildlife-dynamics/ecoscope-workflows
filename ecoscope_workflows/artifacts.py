import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    pass
else:
    pass

from pydantic import Field, BaseModel


class Dags(BaseModel):
    """Target directory for the generated DAGs."""

    jupytext: str = Field(..., alias="jupytext.py")
    script_async_mock_io: str = Field(..., alias="script-async.mock-io.py")
    script_async: str = Field(..., alias="script-async.py")
    script_sequential_mock_io: str = Field(..., alias="script-sequential.mock-io.py")
    script_sequential: str = Field(..., alias="script-sequential.py")


class SymlinkVendor:
    pass


class PixiToml(BaseModel):
    """The pixi.toml file that specifies the workflow."""

    name: str
    version: (
        str  # this can passthrough from the spec.yaml; like conda recipe build numbers
    )
    description: str
    dependencies: list[str]


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
            root.rmdir()
        root.joinpath("dags").mkdir(parents=True)
        for fname, content in self.dags.model_dump(by_alias=True).items():
            root.joinpath("dags").joinpath(fname).write_text(content)
        # self.dags.dump(path / "dags")
        # self.pixi_toml.dump(path / "pixi.toml")

        # with path.joinpath("params.jsonschema").open("w") as f:
        #     json.dump(self.params_jsonschema, f, indent=2)
