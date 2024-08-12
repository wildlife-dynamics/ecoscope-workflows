import pandas as pd
import pytest

from ecoscope_workflows.tasks.transformation import map_values


@pytest.fixture
def sample_df():
    """Fixture to create a sample DataFrame."""
    return pd.DataFrame({"category": ["A", "B", "C", "D"]})


@pytest.fixture
def value_map():
    """Fixture to create a sample value map."""
    return {"A": "Alpha", "B": "Beta"}


def test_map_values_preserve_false(sample_df, value_map):
    """Test value mapping without preserving values not in the map."""
    result_df = map_values(sample_df, "category", value_map, preserve_values=False)
    expected_df = pd.DataFrame(
        {
            "category": [
                "Alpha",
                "Beta",
                None,
                None,
            ]  # Assuming non-mapped values are set to None
        }
    )
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_map_values_preserve_true(sample_df, value_map):
    """Test value mapping with preserving values not in the map."""
    result_df = map_values(sample_df, "category", value_map, preserve_values=True)
    expected_df = pd.DataFrame(
        {"category": ["Alpha", "Beta", "C", "D"]}  # Non-mapped values are preserved
    )
    pd.testing.assert_frame_equal(result_df, expected_df)
