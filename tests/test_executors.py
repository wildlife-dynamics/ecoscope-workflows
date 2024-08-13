from ecoscope_workflows.decorators import task
from ecoscope_workflows.executors import LithopsExecutor, PythonExecutor


def test_python_executor():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    f.executor = PythonExecutor()
    assert f(1, 2) == 3


def test_lithops_executor_sync():
    @task
    def f(a: int, b: int) -> int:
        return a + b

    f.executor = LithopsExecutor(mode="sync")
    assert f.call(1, 2) == 3
