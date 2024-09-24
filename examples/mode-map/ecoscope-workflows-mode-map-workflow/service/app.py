import hashlib
import json
import os
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal

import httpx
import yaml
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field, HttpUrl, SecretStr


app = FastAPI(
    title="Ecoscope Workflows Script Runner",
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


class File(BaseModel):
    name: str
    path: str
    sha: str
    size: int
    download_url: str
    type: Literal["file"] = "file"


class Files(BaseModel):
    script_async: File = Field(alias="script_async.py")
    script_async_mock: File = Field(alias="script_async.mock.py")
    script_sequential: File = Field(alias="script_sequential.py")
    script_sequential_mock: File = Field(alias="script_sequential.mock.py")
    parameters_jsonschema: File = Field(alias="parameters_jsonschema.json")
    environment: File = Field(alias="environment.yml")

    @classmethod
    def from_json(
        cls,
        files: list[dict],
        build_dir_schema_version: int,
    ) -> "Files":
        match build_dir_schema_version:
            case 0:
                return cls(**{f["name"]: f for f in files})
            case _:
                raise ValueError(
                    f"Unsupported build dir schema version: {build_dir_schema_version}"
                )


class BuildFilesStorageBackend(ABC):
    @abstractmethod
    def fetch_files(
        self,
        ref: str,
        build_dir: str,
        build_dir_schema_version: int,
    ) -> Files: ...

    @abstractmethod
    def get_file_content(self, file: File) -> str: ...


def check_env_exists(name: str) -> bool:
    # TODO: consider risks of using shell=True here (required for invoking `micromamba`)
    # question: do we need to explicitly use an initialized `popen.shell` to run `micromamba`?
    exists = subprocess.run(f"micromamba env list | grep -q '{name } '", shell=True)
    return exists.returncode == 0


class GitHubRepository(BaseModel):
    owner: str
    name: str
    host: str = "api.github.com"

    @property
    def api_url(self) -> str:
        return f"https://{self.host}/repos/{self.owner}/{self.name}"


class GitHubStorageBackend(BaseModel, BuildFilesStorageBackend):
    repo: GitHubRepository
    token: SecretStr

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token.get_secret_value()}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def fetch_files(
        self,
        ref: str,
        build_dir: str,
        build_dir_schema_version: int,
    ) -> Files:
        path = f"{self.repo.api_url}/contents/{build_dir}"
        response = httpx.get(path, headers=self.headers, params={"ref": ref})
        response.raise_for_status()  # FIXME: handle non-200 response
        return Files.from_json(
            files=response.json(), build_dir_schema_version=build_dir_schema_version
        )

    def get_file_content(self, file: File) -> str:
        response = httpx.get(file.download_url, headers=self.headers)
        response.raise_for_status()  # FIXME: handle non-200 response
        return response.text


class Build(BaseModel):
    storage_backend: GitHubStorageBackend
    ref: str
    build_dir: str = "build"
    build_dir_schema_version: int = 0

    def fetch_files(self) -> Files:
        return self.storage_backend.fetch_files(
            self.ref,
            self.build_dir,
            self.build_dir_schema_version,
        )

    def get_file_content(self, file: File) -> str:
        return self.storage_backend.get_file_content(file)


class Params(BaseModel):
    config_file_params: dict
    data_connections_env_vars: dict[str, SecretStr]


class Script(BaseModel):
    build: Build
    script_type: Literal["async", "async_mock", "sequential", "sequential_mock"]
    params: Params


class EcoscopeServer(BaseModel):
    api_version: int
    workflow_run_id: str
    base_url: HttpUrl
    token: SecretStr

    @property
    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token.get_secret_value()}",
        }

    @property
    def update_results_endpoint(self) -> str:
        return f"{self.base_url}/v{self.api_version}/workflow_runs/{self.workflow_run_id}/result"


class PopenEnv(BaseModel):
    ECOSCOPE_WORKFLOWS_RESULTS: str  # bucket for storing workflow results


class Popen(BaseModel):
    shell: str
    mamba_exe: str
    env: PopenEnv


class Runner(BaseModel):
    popen: Popen
    ecoscope_server: EcoscopeServer


class WorkflowProcess(BaseModel):
    returncode: int
    stderr: str | None


class UpdateResults(BaseModel):
    status_code: int
    detail: str | None


class RunScriptResponse(BaseModel):
    workflow_process: WorkflowProcess
    update_results: UpdateResults


@app.post(
    "/", response_model=RunScriptResponse, status_code=200
)  # TODO: authenticate requests
def run_script(script: Script, runner: Runner, response: Response):
    """Fetch and run a script with parameters and update the results on Ecoscope Server."""

    files = script.build.fetch_files()
    # at docker build time, we will have created a selection of conda environments to choose from.
    # based on the environment checksum, we will select the appropriate environment to run the script.
    environment_file_content = script.build.get_file_content(files.environment)
    env_name = (
        "env-" + hashlib.sha256(environment_file_content.encode()).hexdigest()[:7]
    )
    if not check_env_exists(env_name):
        # TODO: Better error handling for missing environment
        raise ValueError(f"Environment {env_name} does not exist")

    tmp = Path(os.environ.get("TMPDIR", "/tmp"))
    script_tmp = tmp / "script.py"
    script_file = getattr(files, f"script_{script.script_type}")
    script_content = script.build.get_file_content(script_file)
    script_tmp.write_text(script_content)

    # TODO: use parameters jsonschema to validate config_file_params
    config_tmp = tmp / "config.yaml"
    config_tmp.write_text(yaml.dump(script.params.config_file_params))

    cmd = " ".join(
        [
            # we select the shell explicitly because mamba needs to be initialized
            # with the shell in order to run the script. this will need to be part
            # of the build process for the container that runs this script.
            runner.popen.shell,
            "-c",
            f"'{runner.popen.mamba_exe} run -n {env_name} python",
            script_tmp.as_posix(),
            "--config-file",
            f"{config_tmp.as_posix()}'",
        ],
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
