import re

import pytest

from ecoscope_workflows.tasks.results import (
    create_widget_single_view,
    merge_widget_views,
)
from ecoscope_workflows.tasks.results._widgets import GroupedWidget, WidgetSingleView


def test_create_widget_single_view():
    widget_type = "map"
    title = "A Great Map"
    filter = (("month", "=", "january"), ("year", "=", "2022"))
    data = "<div>Map</div>"

    widget = create_widget_single_view(widget_type, title, filter, data)
    assert widget == WidgetSingleView(
        widget_type=widget_type,
        title=title,
        view=filter,
        data=data,
    )


def test_grouped_widget_merge():
    widget1 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "<div>Map jan</div>",
            ("month", "=", "february"): "<div>Map feb</div>",
        },
    )
    widget2 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "march"): "<div>Map mar</div>",
            ("month", "=", "april"): "<div>Map apr</div>",
        },
    )
    widget1 |= widget2
    assert widget1 == GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "<div>Map jan</div>",
            ("month", "=", "february"): "<div>Map feb</div>",
            ("month", "=", "march"): "<div>Map mar</div>",
            ("month", "=", "april"): "<div>Map apr</div>",
        },
    )


def test_grouped_widget_incompatible_merge_raises():
    widget1 = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "<div>Map jan</div>",
            ("month", "=", "february"): "<div>Map feb</div>",
        },
    )
    widget2 = GroupedWidget(
        widget_type="map",
        title="A Better Map",
        views={
            ("month", "=", "march"): "<div>Map mar</div>",
            ("month", "=", "april"): "<div>Map apr</div>",
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
        data="<div>Map jan</div>",
    )
    view2 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "february"),
        data="<div>Map feb</div>",
    )
    merged = merge_widget_views([view1, view2])
    assert merged == [
        GroupedWidget(
            widget_type="map",
            title="A Great Map",
            views={
                ("month", "=", "january"): "<div>Map jan</div>",
                ("month", "=", "february"): "<div>Map feb</div>",
            },
        ),
    ]


def test_merge_widget_views_multiple_widgets():
    widget1_view1 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="<div>Map jan</div>",
    )
    widget1_view2 = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "february"),
        data="<div>Map feb</div>",
    )
    widget2_view1 = WidgetSingleView(
        widget_type="plot",
        title="Super Cool Plot",
        view=("month", "=", "january"),
        data="<div>Plot jan</div>",
    )
    widget2_view2 = WidgetSingleView(
        widget_type="plot",
        title="Super Cool Plot",
        view=("month", "=", "february"),
        data="<div>Plot feb</div>",
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
                ("month", "=", "january"): "<div>Map jan</div>",
                ("month", "=", "february"): "<div>Map feb</div>",
            },
        ),
        GroupedWidget(
            widget_type="plot",
            title="Super Cool Plot",
            views={
                ("month", "=", "january"): "<div>Plot jan</div>",
                ("month", "=", "february"): "<div>Plot feb</div>",
            },
        ),
    ]


def test_grouped_widget_get_view():
    grouped = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "<div>Map jan</div>",
            ("month", "=", "february"): "<div>Map feb</div>",
        },
    )
    view = grouped.get_view(("month", "=", "january"))
    assert view == WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="<div>Map jan</div>",
    )
