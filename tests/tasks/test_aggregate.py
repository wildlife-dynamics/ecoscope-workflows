import pandas as pd
import pytest

from ecoscope_workflows.tasks.analysis import aggregate


def test_count():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "count")
    pd.testing.assert_series_equal(result, pd.Series({"data_count": 3}))


def test_mean():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "mean")
    pd.testing.assert_series_equal(result, pd.Series({"data_mean": 2.0}))


def test_sum():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "sum")
    pd.testing.assert_series_equal(result, pd.Series({"data_sum": 6}))


def test_invalid_function():
    df = pd.DataFrame({"data": [1, 2, 3]})
    with pytest.raises(ValueError):
        aggregate(df, "data", "invalid_function")
