import pandas as pd
import pytest

from ecoscope_workflows_core.tasks.analysis import (
    apply_arithmetic_operation,
    dataframe_column_mean,
    dataframe_column_max,
    dataframe_column_min,
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


def test_max():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = dataframe_column_max(df, "data")
    assert result == 3


def test_min():
    df = pd.DataFrame({"data": [1, 2, 3]})
    result = dataframe_column_min(df, "data")
    assert result == 1


def test_nunique():
    df = pd.DataFrame({"data": [1, 2, 3, 1]})
    result = dataframe_column_nunique(df, "data")
    assert result == 3


@pytest.mark.parametrize(
    "a, b, operation, expected",
    [
        (1, 2, "add", 3),
        (3, 2, "subtract", 1),
        (2, 3, "multiply", 6),
        (6, 3, "divide", 2),
        (7, 3, "floor_divide", 2),
        (7, 3, "modulo", 1),
        (2, 3, "power", 8),
    ],
)
def test_apply_arithmetic_operation(a, b, operation, expected):
    result = apply_arithmetic_operation(a, b, operation)
    assert result == expected
