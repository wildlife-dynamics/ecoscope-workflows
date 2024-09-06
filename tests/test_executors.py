import os
import pathlib
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


@pytest.fixture
def lithops_env(tmp_path: pathlib.Path) -> dict:
    conf = {
        "lithops": {
            "backend": "localhost",
            "storage": "localhost",
        },
        "localhost": {
            "runtime": sys.executable,
        },
    }
    lithops_dst = tmp_path / "lithops.yaml"
    with open(lithops_dst, mode="w") as of:
        yaml.dump(conf, of)

    return {"LITHOPS_CONFIG_FILE": lithops_dst.as_posix()}


def test_lithops_executor_basic(lithops_env: dict):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    with mock.patch.dict(os.environ, lithops_env):
        f_new = f.set_executor("lithops")
        future = f_new(a=1, b=2)
        res = future.gather()
        assert res == 3


def test_lithops_executor_validate(lithops_env: dict):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    with mock.patch.dict(os.environ, lithops_env):
        future = f.validate().set_executor("lithops")(a="1", b="2")
        res = future.gather()
        assert res == 3


def test_lithops_executor_validate_partial(lithops_env: dict):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    partial = f.validate().partial(b="2")

    with mock.patch.dict(os.environ, lithops_env):
        async_partial = partial.set_executor("lithops")
        future = async_partial.call(a="1")
        res = future.gather()
        assert res == 3


def test_lithops_executor_map(lithops_env: dict):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    with mock.patch.dict(os.environ, lithops_env):
        future = f.set_executor("lithops").map(["a", "b"], [(1, 1), (2, 2), (3, 3)])
        res = future.gather()
        assert res == [2, 4, 6]


def test_lithops_executor_partial_map(lithops_env: dict):
    @task
    def f(a: int, b: int) -> int:
        return a + b

    with mock.patch.dict(os.environ, lithops_env):
        future = (
            f.set_executor("lithops")
            .partial(a=1)
            .map(argnames=["b"], argvalues=[(1,), (2,), (3,)])
        )
        res = future.gather()
        assert res == [2, 3, 4]


def test_lithops_executor_mapvalues(lithops_env: dict):
    @task
    def f(a: int) -> int:
        return a * 2

    with mock.patch.dict(os.environ, lithops_env):
        future = f.set_executor("lithops").mapvalues(
            ["a"],
            [("x", 1), ("y", 2), ("z", 3)],
        )
        res = future.gather()
        assert res == [("x", 2), ("y", 4), ("z", 6)]
