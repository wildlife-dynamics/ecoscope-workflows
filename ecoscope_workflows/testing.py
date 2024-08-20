from unittest.mock import MagicMock, create_autospec

from ecoscope_workflows.decorators import SyncTask
from ecoscope_workflows.util import (
    load_example_return_from_task_reference,
    import_task_from_reference,
)


def create_task_magicmock(anchor: str, func_name: str) -> SyncTask:
    task = import_task_from_reference(anchor, func_name)
    mock_func: MagicMock = create_autospec(spec=task.func)
    example_return = load_example_return_from_task_reference(anchor, func_name)
    mock_func.return_value = example_return

    class MockSyncTask(SyncTask):
        def validate(self):
            return self

    return MockSyncTask(func=mock_func, tags=task.tags, executor=task.executor)
