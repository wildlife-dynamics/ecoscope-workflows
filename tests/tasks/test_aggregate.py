import pandas as pd
import pytest

from ecoscope_workflows.tasks.analysis import aggregate


def test_count():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "count")
    assert result == 3


def test_mean():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "mean")
    assert result == 2.0


def test_sum():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = aggregate(df, "data", "sum")
    assert result == 6


def test_nunique():
    df = pd.DataFrame({"data": [1, 2, 3, 1]})
    result = aggregate(df, "data", "nunique")
    assert result == 3


def test_invalid_function():
    df = pd.DataFrame({"data": [1, 2, 3]})
    with pytest.raises(ValueError):
        aggregate(df, "data", "invalid_function")
