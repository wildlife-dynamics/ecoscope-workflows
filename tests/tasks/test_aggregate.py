import pandas as pd

from ecoscope_workflows.tasks.analysis import (
    dataframe_column_mean,
    dataframe_column_nunique,
    dataframe_column_sum,
    dataframe_count,
)


def test_count():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = dataframe_count(df)
    assert result == 3


def test_mean():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = dataframe_column_mean(df, "data")
    assert result == 2.0


def test_sum():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = dataframe_column_sum(df, "data")
    assert result == 6


def test_nunique():
    df = pd.DataFrame({"data": [1, 2, 3, 1]})
    result = dataframe_column_nunique(df, "data")
    assert result == 3
