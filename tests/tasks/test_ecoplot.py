import pytest
import pandas as pd

from ecoscope_workflows.tasks.results._ecoplot import (
    draw_ecoplot,
    draw_stacked_bar_chart,
)


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "value": [500, 200, 300, 150, 400],
        "category": ["A", "B", "A", "B", "B"],
        "time": [
            pd.to_datetime("2024-06-01", utc=True),
            pd.to_datetime("2024-06-02", utc=True),
            pd.to_datetime("2024-06-03", utc=True),
            pd.to_datetime("2024-06-04", utc=True),
            pd.to_datetime("2024-06-05", utc=True),
        ],
    }

    return pd.DataFrame(data)


@pytest.fixture
def stacked_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "value": [500, 200, 300, 150, 400],
        "category": ["A", "B", "A", "B", "B"],
        "time": [
            pd.to_datetime("2024-06-01", utc=True),
            pd.to_datetime("2024-06-01", utc=True),
            pd.to_datetime("2024-06-02", utc=True),
            pd.to_datetime("2024-06-02", utc=True),
            pd.to_datetime("2024-06-02", utc=True),
        ],
    }

    return pd.DataFrame(data)


def test_draw_ecoplot(sample_dataframe):
    groupby = "category"
    x_axis = "time"
    y_axis = "value"

    plot = draw_ecoplot(
        sample_dataframe,
        group_by=groupby,
        x_axis=x_axis,
        y_axis=y_axis,
        style_kws={"line": {"color": "green"}},
    )

    assert isinstance(plot, str)


def test_draw_stacked_bar_chart(stacked_dataframe):
    plot = draw_stacked_bar_chart(
        stacked_dataframe,
        x_axis="time",
        y_axis="category",
        stack_column="category",
        agg_function="count",
        groupby_style_kws={"A": {"marker_color": "red"}, "B": {"marker_color": "blue"}},
        style_kws={"xperiodalignment": "middle"},
        layout_kws={"xaxis_dtick": 86400000},
    )

    assert isinstance(plot, str)
