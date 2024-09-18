import contextlib
import inspect
import os
import subprocess
import sys
from pathlib import Path

import ruamel.yaml
from pydantic import BaseModel

from ecoscope_workflows.decorators import SyncTask
from ecoscope_workflows.util import (
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

    return MockSyncTask(
        func=mock_func, tags=task.tags, executor=task.executor, requires=task.requires
    )


class Assertions(BaseModel):
    result_stdout_contains: list[str]


class TestCase(BaseModel):
    name: str
    description: str
    params: dict
    assertions: Assertions


def test_case(script: Path, case_name: str, test_cases_yaml: Path, tmp_path: Path):
    """Run a single test case for a workflow script."""

    yaml = ruamel.yaml.YAML(typ="safe")
    all_cases = yaml.load(test_cases_yaml.read_text())
    assert case_name in all_cases, f"{case_name =} not found in {test_cases_yaml =}"
    test_case = TestCase(**all_cases[case_name])
    with tmp_path.joinpath("params.yaml").open("w") as f:
        yaml.dump(test_case.params, f)

    cmd = (
        f"{sys.executable} -W ignore {script.absolute().as_posix()} "
        f"--config-file {tmp_path.joinpath('params.yaml').as_posix()}"
    )
    env = os.environ.copy()
    env["ECOSCOPE_WORKFLOWS_RESULTS"] = tmp_path.as_posix()
    if "async" in script.as_posix() and not os.environ.get("LITHOPS_CONFIG_FILE"):
        # a lithops test is requested but no lithops config is set in the environment
        # users can set this in their environment to avoid this, to test particular
        # lithops configurations. but if they don't, we'll set a default one here.
        lithops_config_outpath = tmp_path / "lithops.yaml"
        lithops_config = {
            "lithops": {
                "backend": "localhost",
                "storage": "localhost",
                "log_level": "INFO",
                "data_limit": 16,
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
        env=env,
    )
    returncode = proc.wait()
    if returncode != 0:
        assert proc.stderr is not None
        raise ValueError(f"{cmd = } failed with:\n {proc.stderr.read()}")
    assert returncode == 0
    assert proc.stdout is not None
    stdout = proc.stdout.read().strip()
    for expected_substring in test_case.assertions.result_stdout_contains:
        assert expected_substring in stdout


@contextlib.contextmanager
def pixienv(path: Path):
    sys.path.insert(0, path.as_posix())
    yield
    sys.path.remove(path.as_posix())
