from pydantic import BaseModel


class Dags(BaseModel):
    """The target directory for the generated DAGs."""

    jupytext: str
    script_async_mock_io: str
    script_async: str
    script_sequential_mock_io: str
    script_sequential: str


class SymlinkVendor:
    pass


class WorkflowArtifacts(BaseModel):
    """The target directory for Pixi."""

    dags: Dags
    src: SymlinkVendor | None = None
    test: ...
    params_jsonschema: dict
    pixi_toml: dict  # if SymlinkVendor is None, we can simplify this and just install a release of workflows from prefix.dev
