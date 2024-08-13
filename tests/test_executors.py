from dataclasses import FrozenInstanceError

import pytest

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


def test_lithops_executor():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    f_new = f.set_executor("lithops")
    future = f_new(1, 2)
    assert future.gather() == 3
