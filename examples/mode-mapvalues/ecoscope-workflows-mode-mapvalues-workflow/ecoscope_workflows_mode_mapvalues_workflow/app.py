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

    if execution_mode == "async":
        if not lithops_config:
            lithops_config = LithopsConfig()
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".yaml"
        ) as lithops_config_file:
            yaml.dump(lithops_config.model_dump(), lithops_config_file)

    update_env = {
        "ECOSCOPE_WORKFLOWS_RESULTS": results_url,
        "LITHOPS_CONFIG_FILE": lithops_config_file.name,
    } | (
        {k: v.get_secret_value() for k, v in data_connections_env_vars.items()}
        if data_connections_env_vars
        else {}
    )
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
