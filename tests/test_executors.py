import os
import sys
from unittest import mock
from dataclasses import FrozenInstanceError

import pytest
import yaml

from ecoscope_workflows.decorators import task
from ecoscope_workflows.executors import LithopsExecutor, PythonExecutor


def test_default_python_executor():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    assert isinstance(f.executor, PythonExecutor)
    assert f(1, 2) == 3


def test_reassign_executor_field():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    assert isinstance(f.executor, PythonExecutor)

    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'executor'"):
        f.executor = LithopsExecutor()

    f_new = f.set_executor("lithops")
    assert isinstance(f_new.executor, LithopsExecutor)

    f_roundtripped = f.set_executor("python")
    assert isinstance(f_roundtripped.executor, PythonExecutor)


@pytest.fixture(scope="module")
def lithops_env(tmp_path_factory: pytest.TempPathFactory) -> dict:
    conf = {
        "lithops": {
            "backend": "localhost",
            "storage": "localhost",
        },
        "localhost": {
            "runtime": sys.executable,
        },
    }
    tmp_path = tmp_path_factory.mktemp("lithops")
    lithops_dst = tmp_path / "lithops.yaml"
    with open(lithops_dst, mode="w") as of:
        yaml.dump(conf, of)

    return {"LITHOPS_CONFIG_FILE": lithops_dst.as_posix()}


@pytest.fixture(scope="module")
def lithops_executor(lithops_env: dict):
    with mock.patch.dict(os.environ, lithops_env):
        yield LithopsExecutor()


def test_lithops_executor_basic(lithops_executor: LithopsExecutor):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    f_new = f.set_executor(lithops_executor)
    future = f_new(a=1, b=2)
    res = future.gather()
    assert res == 3


def test_lithops_executor_validate(lithops_executor: LithopsExecutor):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    future = f.validate().set_executor(lithops_executor)(a="1", b="2")
    res = future.gather()
    assert res == 3


def test_lithops_executor_validate_partial(lithops_executor: LithopsExecutor):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    partial = f.validate().partial(b="2")

    async_partial = partial.set_executor(lithops_executor)
    future = async_partial.call(a="1")
    res = future.gather()
    assert res == 3


def test_lithops_executor_map(lithops_executor: LithopsExecutor):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    future = f.set_executor(lithops_executor).map(["a", "b"], [(1, 1), (2, 2), (3, 3)])
    res = future.gather()
    assert res == [2, 4, 6]


def test_lithops_executor_partial_map(lithops_executor: LithopsExecutor):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    future = (
        f.set_executor(lithops_executor)
        .partial(a=1)
        .map(argnames=["b"], argvalues=[(1,), (2,), (3,)])
    )
    res = future.gather()
    assert res == [2, 3, 4]


def test_lithops_executor_mapvalues(lithops_executor: LithopsExecutor):
    @task
    def f(a: int) -> int:
        return a * 2

    future = f.set_executor(lithops_executor).mapvalues(
        ["a"],
        [("x", 1), ("y", 2), ("z", 3)],
    )
    res = future.gather()
    assert res == [("x", 2), ("y", 4), ("z", 6)]
