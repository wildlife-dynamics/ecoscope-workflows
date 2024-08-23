import subprocess

import yaml
from pydantic import BaseModel


class MicromambaEnvExportDependency(BaseModel): ...


class MicromambaEnvExport(BaseModel):
    name: str
    channels: list[str]
    dependencies: list[str]


def mamba_env_export() -> MicromambaEnvExport:
    export = subprocess.check_output("micromamba env export").decode("utf-8")
    return MicromambaEnvExport(**yaml.safe_load(export))
