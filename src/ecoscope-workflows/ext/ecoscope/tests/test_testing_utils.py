import pandas as pd

from ecoscope_workflows.core.testing import MockSyncTask, create_task_magicmock
from ecoscope_workflows.core.util import load_example_return_from_task_reference


def test_create_task_magicmock():
    anchor = "ecoscope_workflows.ext.ecoscope.tasks.io"
    func_name = "get_subjectgroup_observations"
    get_subjectgroup_observations = create_task_magicmock(anchor, func_name)
    assert isinstance(get_subjectgroup_observations, MockSyncTask)
    result = get_subjectgroup_observations()
    expected = load_example_return_from_task_reference(anchor, func_name)
    pd.testing.assert_frame_equal(result, expected)


def test_create_task_magicmock_lithops_executor():
    anchor = "ecoscope_workflows.ext.ecoscope.tasks.io"
    func_name = "get_subjectgroup_observations"
    get_subjectgroup_observations = create_task_magicmock(anchor, func_name)
    assert isinstance(get_subjectgroup_observations, MockSyncTask)
    # lithops does its own argument validation so even though this is a mock, to get passed
    # the validation we need to pass the correct arguments, but the actual values don't matter
    kws = {
        "client": 0,
        "subject_group_name": 1,
        "since": 2,
        "until": 3,
        "include_inactive": 4,
    }
    future = get_subjectgroup_observations.set_executor("lithops").call(**kws)
    result = future.gather()
    expected = load_example_return_from_task_reference(anchor, func_name)
    pd.testing.assert_frame_equal(result, expected)
