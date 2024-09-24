import os
import subprocess
import sys
import tempfile
import time
from typing import Literal

import ruamel.yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, SecretStr


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
    entrypoint: str,
    params: dict,
    data_connections_env_vars: dict[str, SecretStr],
    execution_mode: Literal["async", "sequential"],
    mock_io: bool,
    results_url: str,
    lithops_config: LithopsConfig,
    callback_url: str,  # TODO: authenticatation (hmac)
):
    yaml = ruamel.yaml.YAML(typ="safe")
    # TODO: use parameters jsonschema to validate config_file_params
    # OH WOW WE COULD GENERATE A PYDANTIC MODEL FROM THE PARAMS JSONSCHEMA AND USE THAT TO VALIDATE THE INPUT
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as config_file:
        yaml.dump(params, config_file)

    cmd = (
        f"pixi run -e default {entrypoint} "
        f"--config-file {config_file.name} "
        f"--execution-mode {execution_mode} "
        f'{("--mock-io" if mock_io else "--no-mock-io")}'
    )
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".yaml"
    ) as lithops_config_file:
        yaml.dump(lithops_config.model_dump(), lithops_config_file)

    env = (
        os.environ.copy()  # TODO: just copy PATH (not everything) from outer env?
        | {k: v.get_secret_value() for k, v in data_connections_env_vars.items()}
        | {"ECOSCOPE_WORKFLOWS_RESULTS": results_url}
        | {"LITHOPS_CONFIG_FILE": lithops_config_file.name}
    )
    stdout_logfile = os.environ.get(
        "STDOUT_LOGFILE", "/tmp/stdout.log"
    )  # TODO: figure out where we want to store logs
    stderr_logfile = os.environ.get(
        "STDERR_LOGFILE", "/tmp/stderr.log"
    )  # TODO: figure out where we want to store logs
    with (
        open(stdout_logfile, "w") as stdout_writer,
        open(stdout_logfile, "r", 1) as stdout_reader,
        open(stderr_logfile, "w") as stderr_writer,
        open(stderr_logfile, "r", 1) as stderr_reader,
    ):
        # start the process, and `tee` the output of both stdout and stderr to separate log files
        # that are also streamed back to the server process as they are written. this gives us a
        # persisted copy of the logs for recovering later, and also realtime feedback, for anyone
        # watching the server logs.
        proc = subprocess.Popen(
            cmd,
            stdout=stdout_writer,
            stderr=stderr_writer,
            env=env,
            text=True,
        )
        while proc.poll() is None:
            # stream from buffers to stdout/stderr
            sys.stdout.write(stdout_reader.read())
            sys.stderr.write(stderr_reader.read())
            # wait for more output to be available
            time.sleep(0.5)
        # after process exits, write any remaining output
        sys.stdout.write(stdout_reader.read())
        sys.stderr.write(stderr_reader.read())
    returncode = proc.wait()
    with (
        open(stdout_logfile, "r") as completed_proc_stdout_reader,
        open(stderr_logfile, "r") as completed_proc_stderr_reader,
    ):
        # the process has exited, so we can read back the full output
        # from the log files for handling in the response below.
        proc_stdout = completed_proc_stdout_reader.read()
        proc_stderr = completed_proc_stderr_reader.read()
    # match returncode, proc_stdout, proc_stderr:
    #     case (
    #         0,  # exited success
    #         str(),  # there is stdout
    #         stderr,  # there might be stderr (i.e. warnings)
    #     ):
    #         patch_response = httpx.patch(
    #             callback_url,
    #             headers=runner.ecoscope_server.headers,
    #             content=json.dumps(proc_stdout, default=str).encode("utf-8"),
    #         )
    #         # TODO: handle case of non-200 response; implies needing to re-run workflow?
    #         # Maybe re-running is not a big deal if we've cached the result, and is more
    #         # stable than trying to recover from a failed update.
    #         status_code = patch_response.status_code
    #         detail = patch_response.text if status_code != 200 else None
    #     case _, _, str():
    #         stderr = proc_stderr
    #         status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #         detail = None
    #         response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    #     case _, _, _:
    #         stderr = "Unknown error"
    #         status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    #         detail = None
    #         response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return {
        "returncode": returncode,
        "proc_stdout": proc_stdout,
        "proc_stderr": proc_stderr,
    }
