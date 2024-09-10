from dataclasses import FrozenInstanceError

import pytest

from ecoscope_workflows.core.decorators import task
from ecoscope_workflows.core.executors import LithopsExecutor, PythonExecutor


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


def test_lithops_executor_basic():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    f_new = f.set_executor("lithops")
    future = f_new(a=1, b=2)
    assert future.gather() == 3


def test_lithops_executor_validate():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    future = f.validate().set_executor("lithops")(a="1", b="2")
    assert future.gather() == 3


def test_lithops_executor_validate_partial():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    partial = f.validate().partial(b="2")
    async_partial = partial.set_executor("lithops")
    future = async_partial.call(a="1")
    assert future.gather() == 3


def test_lithops_executor_map():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    lithops_executor = LithopsExecutor()
    future = f.set_executor(lithops_executor).map(["a", "b"], [(1, 1), (2, 2), (3, 3)])
    assert future.gather() == [2, 4, 6]


def test_lithops_executor_partial_map():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    lithops_executor = LithopsExecutor()
    future = (
        f.set_executor(lithops_executor)
        .partial(a=1)
        .map(argnames=["b"], argvalues=[(1,), (2,), (3,)])
    )
    assert future.gather() == [2, 3, 4]


def test_lithops_executor_mapvalues():
    @task
    def f(a: int) -> int:
        return a * 2

    lithops_executor = LithopsExecutor()
    future = f.set_executor(lithops_executor).mapvalues(
        ["a"],
        [("x", 1), ("y", 2), ("z", 3)],
    )
    assert future.gather() == [("x", 2), ("y", 4), ("z", 6)]
