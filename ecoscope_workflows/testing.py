from typing import Protocol
from unittest.mock import MagicMock, create_autospec

from ecoscope_workflows.util import (
    load_example_return_from_task_reference,
    import_task_from_reference,
)


class MockWrappedFunctionProtocol(Protocol):
    return_value: MagicMock

    def __call__(self, *args, **kws):
        """Mocks the call signature of a function decorated by `@task`.
        These functions can have arbitrary signatures, so we use `*args` and `**kws`.
        """
        ...


class MockReturnsMutatedTaskCopyProtocol(Protocol):
    return_value: "TaskMagicMock"

    def __call__(self) -> "TaskMagicMock": ...

    def call(self, *args, **kws) -> "TaskMagicMock": ...


class TaskMagicMock(MagicMock):
    validate: MockReturnsMutatedTaskCopyProtocol
    set_executor: MockReturnsMutatedTaskCopyProtocol
    call: MockWrappedFunctionProtocol


def create_task_magicmock(anchor: str, func_name: str) -> TaskMagicMock:
    task = import_task_from_reference(anchor, func_name)
    # the base `task`
    mock_task_0: TaskMagicMock = create_autospec(spec=task)
    # the new task returned by `task.validate()`
    mock_task_1: TaskMagicMock = create_autospec(spec=task)
    mock_task_0.validate.return_value = mock_task_1
    # setup the signature of `task.validate().call`
    mock_task_1.call = create_autospec(spec=task.func)
    # assign the return value of `task.validate().call()`
    example_return = load_example_return_from_task_reference(anchor, func_name)
    mock_task_1.call.return_value = example_return
    # return the base `task`
    return mock_task_0
