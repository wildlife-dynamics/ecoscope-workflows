import pandas as pd
import pytest

from ecoscope_workflows.core.tasks.transformation import map_columns


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    data = {"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]}
    return pd.DataFrame(data)


def test_drop_columns(sample_dataframe):
    """Test that columns are correctly dropped."""
    result_df = map_columns(
        sample_dataframe, drop_columns=["A"], retain_columns=[], rename_columns={}
    )
    assert "A" not in result_df.columns


def test_drop_columns_error(sample_dataframe):
    """Test raising error if a column does not exist."""
    with pytest.raises(KeyError):
        map_columns(
            sample_dataframe,
            drop_columns=["NOT_EXIST"],
            retain_columns=[],
            rename_columns={},
        )


def test_retain_columns(sample_dataframe):
    """Test that only specified columns are retained."""
    result_df = map_columns(
        sample_dataframe, drop_columns=[], retain_columns=["B"], rename_columns={}
    )
    assert list(result_df.columns) == ["B"]


def test_reorder_columns(sample_dataframe):
    """Test that only specified columns are retained."""
    result_df = map_columns(
        sample_dataframe, drop_columns=[], retain_columns=["B", "A"], rename_columns={}
    )
    assert list(result_df.columns) == ["B", "A"]


def test_retain_columns_error(sample_dataframe):
    """Test raising error if a column does not exist."""
    with pytest.raises(KeyError):
        map_columns(
            sample_dataframe,
            drop_columns=[],
            retain_columns=["NOT_EXIST"],
            rename_columns={},
        )


def test_rename_columns(sample_dataframe):
    """Test that columns are correctly renamed."""
    result_df = map_columns(
        sample_dataframe, drop_columns=[], retain_columns=[], rename_columns={"B": "Z"}
    )
    assert "Z" in result_df.columns and "B" not in result_df.columns


def test_rename_columns_error(sample_dataframe):
    """Test raising error if a column does not exist."""
    with pytest.raises(KeyError):
        map_columns(
            sample_dataframe,
            drop_columns=[],
            retain_columns=[],
            rename_columns={"NOT_EXIST": "Z"},
        )


def test_map_columns(sample_dataframe):
    """Test that columns are correctly mapped."""
    result_df = map_columns(
        sample_dataframe,
        drop_columns=["C"],
        retain_columns=["B"],
        rename_columns={"B": "Z"},
    )
    assert list(result_df.columns) == ["Z"]
