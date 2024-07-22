import re

import pytest

from ecoscope_workflows.tasks.results import (
    create_map_widget_single_view,
    create_plot_widget_single_view,
    create_text_widget_single_view,
    create_single_value_widget_single_view,
    merge_widget_views,
)
from ecoscope_workflows.tasks.results._widgets import GroupedWidget, WidgetSingleView


def test_create_map_widget_single_view():
    title = "A Great Map"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = "/path/to/precomputed/jan/2022/map.html"

    widget = create_map_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="map",
        title=title,
        data=data,
        view=view,
    )


def test_create_plot_widget_single_view():
    title = "A Great Plot"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = "/path/to/precomputed/jan/2022/plot.html"

    widget = create_plot_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="plot",
        title=title,
        data=data,
        view=view,
    )


def test_create_text_widget_single_view():
    title = "A Great Text"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = "This is some text."

    widget = create_text_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="text",
        title=title,
        data=data,
        view=view,
    )


def test_create_single_value_widget_single_view():
    title = "A Great Value"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = 123.45

    widget = create_single_value_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="single_value",
        title=title,
        data=data,
        view=view,
    )


def test_grouped_widget_merge():
    widget1 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
            ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
        },
    )
    widget2 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "march"): "/path/to/precomputed/mar/map.html",
            ("month", "=", "april"): "/path/to/precomputed/apr/map.html",
        },
    )
    widget1 |= widget2
    assert widget1 == GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
            ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
            ("month", "=", "march"): "/path/to/precomputed/mar/map.html",
            ("month", "=", "april"): "/path/to/precomputed/apr/map.html",
        },
    )


def test_grouped_widget_incompatible_merge_raises():
    widget1 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
            ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
        },
    )
    widget2 = GroupedWidget(
        widget_type="map",
        title="A Better Map",
        views={
            ("month", "=", "march"): "/path/to/precomputed/mar/map.html",
            ("month", "=", "april"): "/path/to/precomputed/apr/map.html",
        },
    )
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Cannot merge GroupedWidgets with different merge keys: "
            "('map', 'A Great Map') != ('map', 'A Better Map')"
        ),
    ):
        widget1 |= widget2


def test_merge_widget_views():
    view1 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="/path/to/precomputed/jan/map.html",
    )
    view2 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "february"),
        data="/path/to/precomputed/feb/map.html",
    )
    merged = merge_widget_views([view1, view2])
    assert merged == [
        GroupedWidget(
            widget_type="map",
            title="A Great Map",
            views={
                ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
                ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
            },
        ),
    ]


def test_merge_widget_views_multiple_widgets():
    widget1_view1 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="/path/to/precomputed/jan/map.html",
    )
    widget1_view2 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "february"),
        data="/path/to/precomputed/feb/map.html",
    )
    widget2_view1 = WidgetSingleView(
        widget_type="plot",
        title="Super Cool Plot",
        view=("month", "=", "january"),
        data="/path/to/precomputed/jan/plot.html",
    )
    widget2_view2 = WidgetSingleView(
        widget_type="plot",
        title="Super Cool Plot",
        view=("month", "=", "february"),
        data="/path/to/precomputed/feb/plot.html",
    )
    merged = merge_widget_views(
        [
            widget1_view1,
            widget1_view2,
            widget2_view1,
            widget2_view2,
        ]
    )
    assert merged == [
        GroupedWidget(
            widget_type="map",
            title="A Great Map",
            views={
                ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
                ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
            },
        ),
        GroupedWidget(
            widget_type="plot",
            title="Super Cool Plot",
            views={
                ("month", "=", "january"): "/path/to/precomputed/jan/plot.html",
                ("month", "=", "february"): "/path/to/precomputed/feb/plot.html",
            },
        ),
    ]


def test_grouped_widget_get_view():
    grouped = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
            ("month", "=", "february"): "/path/to/precomputed/feb/map.html",
        },
    )
    view = grouped.get_view(("month", "=", "january"))
    assert view == WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="/path/to/precomputed/jan/map.html",
    )
