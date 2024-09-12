import inspect

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

    return MockSyncTask(func=mock_func, tags=task.tags, executor=task.executor)


class TestCase(BaseModel):
    name: str
    params: dict
    asserts: list
