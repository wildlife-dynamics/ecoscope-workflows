import pandas as pd
import pytest

from ecoscope_workflows.tasks.transformation import filter_dataframe


@pytest.fixture
def sample_df():
    """Fixture to create a sample DataFrame."""
    data = {
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [24, 30, 35, 40, 28],
        "city": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    }
    return pd.DataFrame(data)


def test_filter_dataframe_simple_expression(sample_df):
    """Test filtering with a simple expression."""
    filtered_df = filter_dataframe(sample_df, "age > 30")
    expected_df = sample_df.query("age > 30")
    pd.testing.assert_frame_equal(filtered_df, expected_df)


def test_filter_dataframe_complex_expression(sample_df):
    """Test filtering with a complex expression."""
    filtered_df = filter_dataframe(sample_df, "age > 30 and city == 'Chicago'")
    expected_df = sample_df.query("age > 30 and city == 'Chicago'")
    pd.testing.assert_frame_equal(filtered_df, expected_df)


def test_filter_dataframe_invalid_expression(sample_df):
    """Test handling of invalid expressions."""
    with pytest.raises(SyntaxError):
        filter_dataframe(sample_df, "this is NOT a valid expression")


def test_filter_dataframe_assignment(sample_df):
    """Test handling of invalid expressions."""
    with pytest.raises(SyntaxError):
        filter_dataframe(sample_df, "df['age'] = 100")


def test_filter_dataframe_unsupported_function(sample_df):
    """Test handling of invalid expressions."""
    with pytest.raises(ValueError):
        filter_dataframe(sample_df, "str(age)")
