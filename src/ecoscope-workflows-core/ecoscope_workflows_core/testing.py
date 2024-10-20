import inspect
import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

import ruamel.yaml
from pydantic import BaseModel

from ecoscope_workflows_core.decorators import SyncTask
from ecoscope_workflows_core.util import (
    load_example_return_from_task_reference,
    import_task_from_reference,
)


class MockSyncTask(SyncTask):
    def validate(self) -> "MockSyncTask":
        return self


def create_task_magicmock(anchor: str, func_name: str) -> MockSyncTask:
    task = import_task_from_reference(anchor, func_name)
    example_return = load_example_return_from_task_reference(anchor, func_name)

    def mock_func(*args, **kwargs):
        return example_return

    mock_func.__signature__ = inspect.signature(task.func)  # type: ignore[attr-defined]

    return MockSyncTask(func=mock_func, tags=task.tags, executor=task.executor)


class Assertions(BaseModel):
    result_stdout_contains: list[str]


class TestCase(BaseModel):
    name: str
    description: str
    params: dict
    assertions: Assertions


ExecutionMode = Literal["async", "sequential"]  # TODO: move to executors module


def run_cli_test_case(
    entrypoint: str,
    execution_mode: ExecutionMode,
    mock_io: bool,
    case: TestCase,
    tmp_path: Path,
):
    """Run a single test case for a workflow.

    Args:
        entrypoint (str): The entrypoint of the workflow.
        execution_mode (ExecutionMode): The execution mode to test. One of "async" or "sequential".
        mock_io (bool): Whether or not to mock IO with 3rd party services; for testing only.
        case (TestCase): The test case to run. Test cases are defined by the `test-cases.yaml` file.
        tmp_path (Path): The temporary directory to use for the test.
    """

    yaml = ruamel.yaml.YAML(typ="safe")
    with tmp_path.joinpath("params.yaml").open("w") as f:
        yaml.dump(case.params, f)

    cmd = (
        f"{entrypoint} "
        f"--config-file {tmp_path.joinpath('params.yaml').as_posix()} "
        f"--execution-mode {execution_mode} "
        f'{("--mock-io" if mock_io else "--no-mock-io")}'
    )
    env = os.environ.copy()
    env["ECOSCOPE_WORKFLOWS_RESULTS"] = tmp_path.as_posix()
    if execution_mode == "async" and not os.environ.get("LITHOPS_CONFIG_FILE"):
        # a lithops test is requested but no lithops config is set in the environment
        # users can set this in their environment to avoid this, to test particular
        # lithops configurations. but if they don't, we'll set a default one here.
        lithops_config_outpath = tmp_path / "lithops.yaml"
        lithops_config = {
            "lithops": {
                "backend": "localhost",
                "storage": "localhost",
                "log_level": "INFO",
                "data_limit": 256,
            },
            "localhost": {"runtime": sys.executable},
        }
        yaml = ruamel.yaml.YAML(typ="safe")
        with open(lithops_config_outpath, mode="w") as f:
            yaml.dump(lithops_config, f)

        env["LITHOPS_CONFIG_FILE"] = lithops_config_outpath.as_posix()

    proc = subprocess.Popen(
        cmd.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env | {"PYTHONWARNINGS": "ignore"},
    )
    returncode = proc.wait()
    if returncode != 0:
        assert proc.stderr is not None
        raise ValueError(f"{cmd = } failed with:\n {proc.stderr.read()}")
    assert returncode == 0
    assert proc.stdout is not None
    stdout = proc.stdout.read().strip()
    for expected_substring in case.assertions.result_stdout_contains:
        assert expected_substring in stdout
