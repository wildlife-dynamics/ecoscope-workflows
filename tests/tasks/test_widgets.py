import re

import pytest

from ecoscope_workflows.tasks.results import (
    create_map_widget_single_view,
    create_plot_widget_single_view,
    create_single_value_widget_single_view,
    create_text_widget_single_view,
    merge_widget_views,
)
from ecoscope_workflows.tasks.results._widget_tasks import (
    GroupedWidget,
    WidgetSingleView,
)
from ecoscope_workflows.tasks.transformation._unit import Quantity, Unit


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
    data = Quantity(value=123.45)

    widget = create_single_value_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="single_value",
        title=title,
        data="123.5",
        view=view,
    )


def test_create_single_value_widget_single_view_unit():
    title = "A Great Value"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = Quantity(value=123.45, unit=Unit.HOUR)

    widget = create_single_value_widget_single_view(title, data, view)
    assert widget == WidgetSingleView(
        widget_type="single_value",
        title=title,
        data="123.5 h",
        view=view,
    )


def test_create_single_value_widget_single_view_decimal_places():
    title = "A Great Value"
    view = (("month", "=", "january"), ("year", "=", "2022"))
    data = Quantity(value=123.45, unit=Unit.HOUR)

    widget = create_single_value_widget_single_view(title, data, view, decimal_places=3)
    assert widget == WidgetSingleView(
        widget_type="single_value",
        title=title,
        data="123.450 h",
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


def test_single_view_widget_to_grouped_widget():
    widget = WidgetSingleView(
        widget_type="map",
        title="A Great Map",
        view=("month", "=", "january"),
        data="/path/to/precomputed/jan/map.html",
    )
    grouped = GroupedWidget.from_single_view(widget)
    assert grouped == GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            ("month", "=", "january"): "/path/to/precomputed/jan/map.html",
        },
    )


def test_merge_grouped_widget_views():
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


def test_merge_grouped_widget_views_multiple_widgets():
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
        ],
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


def test_grouped_widget_get_view_none():
    none_view = GroupedWidget(
        widget_type="map",
        title="A map with only one view and no groupers",
        views={
            None: "/path/to/precomputed/single/map.html",
        },
    )
    view = none_view.get_view(None)
    assert view == WidgetSingleView(
        widget_type="map",
        title="A map with only one view and no groupers",
        view=None,
        data="/path/to/precomputed/single/map.html",
    )


def test_merge_grouped_widget_views_multiple_widgets_with_none_views():
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
    widget2_only_view = WidgetSingleView(
        widget_type="map",
        title="A map with only one view and no groupers",
        view=None,
        data="/path/to/precomputed/single/map.html",
    )
    widget3_only_view = WidgetSingleView(
        widget_type="plot",
        title="A plot with only one view and no groupers",
        view=None,
        data="/path/to/precomputed/single/plot.html",
    )
    merged = merge_widget_views(
        [
            widget1_view1,
            widget1_view2,
            widget2_only_view,
            widget3_only_view,
        ],
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
            widget_type="map",
            title="A map with only one view and no groupers",
            views={
                None: "/path/to/precomputed/single/map.html",
            },
        ),
        GroupedWidget(
            widget_type="plot",
            title="A plot with only one view and no groupers",
            views={
                None: "/path/to/precomputed/single/plot.html",
            },
        ),
    ]
