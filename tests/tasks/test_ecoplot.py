import pandas as pd
import pytest

from ecoscope_workflows.tasks.results._ecoplot import (
    GroupedPlotStyle,
    LayoutStyle,
    LineStyle,
    PlotCategoryStyle,
    PlotStyle,
    draw_ecoplot,
    draw_pie_chart,
    draw_time_series_bar_chart,
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
def time_series_dataframe(time_interval):
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "category": ["A", "B", "A", "B", "B"],
    }
    match time_interval:
        case "year":
            data["time"] = [
                pd.to_datetime("2023-06-01 15:33:00", utc=True),
                pd.to_datetime("2023-06-01 15:34:00", utc=True),
                pd.to_datetime("2024-06-02 15:36:00", utc=True),
                pd.to_datetime("2024-06-02 15:37:00", utc=True),
                pd.to_datetime("2024-06-02 15:38:00", utc=True),
            ]
        case "month":
            data["time"] = [
                pd.to_datetime("2024-05-01 15:33:00", utc=True),
                pd.to_datetime("2024-05-01 15:34:00", utc=True),
                pd.to_datetime("2024-06-02 15:36:00", utc=True),
                pd.to_datetime("2024-06-02 15:37:00", utc=True),
                pd.to_datetime("2024-06-02 15:38:00", utc=True),
            ]
        case "week":
            data["time"] = [
                pd.to_datetime("2024-05-06 15:33:00", utc=True),
                pd.to_datetime("2024-05-06 15:34:00", utc=True),
                pd.to_datetime("2024-05-14 15:36:00", utc=True),
                pd.to_datetime("2024-05-14 15:37:00", utc=True),
                pd.to_datetime("2024-05-14 15:38:00", utc=True),
            ]
        case "day":
            data["time"] = [
                pd.to_datetime("2024-05-01 15:33:00", utc=True),
                pd.to_datetime("2024-05-01 15:34:00", utc=True),
                pd.to_datetime("2024-05-02 15:36:00", utc=True),
                pd.to_datetime("2024-05-02 15:37:00", utc=True),
                pd.to_datetime("2024-05-02 15:38:00", utc=True),
            ]
        case "hour":
            data["time"] = [
                pd.to_datetime("2024-05-01 15:33:00", utc=True),
                pd.to_datetime("2024-05-01 15:34:00", utc=True),
                pd.to_datetime("2024-05-01 16:36:00", utc=True),
                pd.to_datetime("2024-05-01 16:37:00", utc=True),
                pd.to_datetime("2024-05-01 16:38:00", utc=True),
            ]

    return pd.DataFrame(data)


@pytest.fixture
def pie_dataframe():
    """Fixture to provide a sample DataFrame for testing."""
    data = {
        "value": [500, 200, 300, 150, 400],
        "category": ["A", "B", "A", "B", "C"],
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
        plot_style=PlotStyle(line_style=LineStyle(color="green")),
    )

    assert isinstance(plot, str)


@pytest.mark.parametrize(
    "time_series_dataframe, time_interval",
    [
        ("year", "year"),
        ("month", "month"),
        ("week", "week"),
        ("day", "day"),
        ("hour", "hour"),
    ],
    indirect=["time_series_dataframe"],
)
def test_draw_time_series_bar_chart(time_series_dataframe, time_interval):
    plot = draw_time_series_bar_chart(
        time_series_dataframe,
        x_axis="time",
        y_axis="category",
        category="category",
        agg_function="count",
        time_interval=time_interval,
        grouped_styles=[
            GroupedPlotStyle(
                category="A", plot_style=PlotCategoryStyle(marker_color="red")
            ),
            GroupedPlotStyle(
                category="B", plot_style=PlotCategoryStyle(marker_color="blue")
            ),
        ],
        plot_style=PlotStyle(xperiodalignment="middle"),
    )

    assert isinstance(plot, str)


def test_draw_pie_chart(pie_dataframe):
    plot = draw_pie_chart(
        pie_dataframe,
        value_column="value",
        label_column="category",
        plot_style=PlotStyle(
            marker_colors=["chartreuse", "red", "magenta"],
            textinfo="value",
        ),
        layout_style=LayoutStyle(font_color="orange", font_style="italic"),
    )

    assert isinstance(plot, str)
    assert isinstance(plot, str)
