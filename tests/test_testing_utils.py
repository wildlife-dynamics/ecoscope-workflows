import pandas as pd

from ecoscope_workflows.testing import MockSyncTask, create_task_magicmock
from ecoscope_workflows.util import load_example_return_from_task_reference


def test_create_task_magicmock():
    anchor = "ecoscope_workflows.tasks.io"
    func_name = "get_subjectgroup_observations"
    get_subjectgroup_observations = create_task_magicmock(anchor, func_name)
    assert isinstance(get_subjectgroup_observations, MockSyncTask)
    result = get_subjectgroup_observations()
    expected = load_example_return_from_task_reference(anchor, func_name)
    pd.testing.assert_frame_equal(result, expected)
