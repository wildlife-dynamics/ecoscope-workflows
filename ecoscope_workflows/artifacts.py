import json
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    pass
else:
    pass

from pydantic import BaseModel


class Dags(BaseModel):
    """Target directory for the generated DAGs."""

    jupytext: str
    script_async_mock_io: str
    script_async: str
    script_sequential_mock_io: str
    script_sequential: str

    def dump(self, path: Path): ...


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

    def dump(self, path: Path): ...


class WorkflowArtifacts(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    dags: Dags
    src: SymlinkVendor | None = None
    test: ...
    params_jsonschema: dict
    pixi_toml: dict  # if SymlinkVendor is None, we can simplify this and just install a release of workflows from prefix.dev

    def dump(self, path: Path):
        self.dags.dump(path / "dags")
        self.pixi_toml.dump(path / "pixi.toml")

        with path.joinpath("params.jsonschema").open("w") as f:
            json.dump(self.params_jsonschema, f, indent=2)
