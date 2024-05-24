from typing import Callable, Protocol
from unittest.mock import MagicMock, create_autospec

from ecoscope_workflows.util import (
    load_example_return_from_task_reference,
    import_distributed_task_from_reference,
)


class MockWrappedFunctionProtocol(Protocol):
    return_value: MagicMock

    def __call__(self, *args, **kws):
        """Mocks the call signature of a function decorated by `@distributed`.
        These functions can have arbitrary signatures, so we use `*args` and `**kws`.
        """
        ...


class MockReplaceProtocol(Protocol):
    return_value: MockWrappedFunctionProtocol

    def __call__(
        self,
        arg_prevalidators: dict[str, Callable] | None = None,
        return_postvalidator: Callable | None = None,
        validate: bool | None = None,
    ) -> "DistributedTaskMagicMock":
        """Mocks the call signature of `distributed.replace`, which returns a mutated
        instance of the `distributed` decorator with the specified changes.
        """
        ...


class DistributedTaskMagicMock(MagicMock):
    replace: MockReplaceProtocol


def create_distributed_task_magicmock(
    anchor: str, func_name: str
) -> DistributedTaskMagicMock:
    spec = import_distributed_task_from_reference(anchor, func_name)
    mock_task: DistributedTaskMagicMock = create_autospec(spec=spec)
    # match the signature of the wrapped function, to require same arguments
    mock_task.replace.return_value = create_autospec(spec=spec.func)
    # load the example return data
    example_return = load_example_return_from_task_reference(anchor, func_name)
    mock_task.replace.return_value.return_value = example_return
    return mock_task
