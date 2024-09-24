import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Literal

import httpx
import yaml
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, SecretStr


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


class Params(BaseModel):
    config_file_params: dict
    data_connections_env_vars: dict[str, SecretStr]


class Run(BaseModel):
    execution_mode: Literal["async", "sequential"]
    mock_io: bool
    params: Params


class WorkflowProcess(BaseModel):
    returncode: int
    stderr: str | None


class UpdateResults(BaseModel):
    status_code: int
    detail: str | None


class RunResponse(BaseModel):
    workflow_process: WorkflowProcess
    update_results: UpdateResults


@app.post("/", response_model=RunResponse, status_code=200)
def run(
    run: Run,
    results_bucket: str,
    callback_url: str,  # TODO: authenticatation (hmac)

):
    """Fetch and run a script with parameters and update the results on Ecoscope Server."""

    tmp = Path(os.environ.get("TMPDIR", "/tmp"))

    # TODO: use parameters jsonschema to validate config_file_params
    config_tmp = tmp / "config.yaml"
    config_tmp.write_text(yaml.dump(script.params.config_file_params))

    cmd = (
        f"{entrypoint} "
        f"--config-file {tmp.joinpath('params.yaml').as_posix()} "
        f"--execution-mode {runner.} "
        f'{("--mock-io" if mock_io else "--no-mock-io")}'
    )
    env = (
        os.environ.copy()  # TODO: just copy PATH (not everything) from outer env?
        | runner.popen.env.model_dump()
        | {
            k: v.get_secret_value()
            for k, v in script.params.data_connections_env_vars.items()
        }
    )
    if "async" in script.script_type:
        lithops_config = {
            # TODO: all/most of this should be configurable
            "lithops": {
                "backend": "gcp_cloudrun",
                "storage": "gcp_storage",
                "log_level": "DEBUG",
                "data_limit": 16,
            },
            "gcp": {
                "region": "us-central1",
                "credentials_path": os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
            },
            "gcp_cloudrun": {
                "runtime": f"us.gcr.io/{os.environ['GCP_PROJECT']}/{env_name}-worker",
                "runtime_cpu": 2,
                "runtime_memory": 1000,
            },
        }
        with open(tmp / "lithops_config.yaml", "w") as f:
            yaml.dump(lithops_config, f)
            env["LITHOPS_CONFIG_FILE"] = f.name

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
            shell=True,  # FIXME: can we avoid shell=True if using mamba?
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
    match returncode, proc_stdout, proc_stderr:
        case (
            0,  # exited success
            str(),  # there is stdout
            stderr,  # there might be stderr (i.e. warnings)
        ):
            patch_response = httpx.patch(
                runner.ecoscope_server.update_results_endpoint,
                headers=runner.ecoscope_server.headers,
                content=json.dumps(proc_stdout, default=str).encode("utf-8"),
            )
            # TODO: handle case of non-200 response; implies needing to re-run workflow?
            # Maybe re-running is not a big deal if we've cached the result, and is more
            # stable than trying to recover from a failed update.
            status_code = patch_response.status_code
            detail = patch_response.text if status_code != 200 else None
        case _, _, str():
            stderr = proc_stderr
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = None
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        case _, _, _:
            stderr = "Unknown error"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = None
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return {
        "workflow_process": {"returncode": returncode, "stderr": stderr},
        "update_results": {"status_code": status_code, "detail": detail},
    }
