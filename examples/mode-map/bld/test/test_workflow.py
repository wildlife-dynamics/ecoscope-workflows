import os
import sys
from pathlib import Path
import subprocess

import pytest
import ruamel.yaml


BLD = Path(__file__).parent.parent
TEST_CASES_YAML = BLD.parent / "test-cases.yaml"


@pytest.mark.parametrize(
    "script",
    [BLD / "dag.script_async.py", BLD / "dag.script_sequential.py"],
    ids=["script-async", "script-sequential"],
)
def test_end_to_end(script: Path, case: str, tmp_path: Path):
    print(f"Running end-to-end test for {script =} with {case =}:")
    yaml = ruamel.yaml.YAML(typ="safe")
    all_cases = yaml.load(TEST_CASES_YAML.read_text())
    assert case in all_cases, f"{case =} not found in {TEST_CASES_YAML =}"
    with tmp_path.joinpath("params.yaml").open("w") as f:
        yaml.dump(all_cases[case]["params"], f)

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
    print(stdout)
    # todo: get asserts from test case
    # for assert_fn in end_to_end.assert_that_stdout:
    #     assert assert_fn(stdout)
