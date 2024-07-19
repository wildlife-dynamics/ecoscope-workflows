from ecoscope_workflows.tasks.results import (
    create_widget_single_view,
    merge_widget_views,
)
from ecoscope_workflows.tasks.results._widgets import GroupedWidget


def test_create_widget_single_view():
    widget_type = "map"
    title = "A Great Map"
    filter = (("month", "=", "january"), ("year", "=", "2022"))
    data = "<div>Map</div>"

    widget = create_widget_single_view(widget_type, title, filter, data)
    assert widget == {
        "widget_type": widget_type,
        "title": title,
        "views": {filter: data},
    }


def test_merge_widget_views():
    view1 = {
        "widget_type": "map",
        "title": "A Great Map",
        "views": {("month", "=", "january"): "<div>Map jan</div>"},
    }
    view2 = {
        "widget_type": "map",
        "title": "A Great Map",
        "views": {("month", "=", "february"): "<div>Map feb</div>"},
    }
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
    widget1_view1 = {
        "widget_type": "map",
        "title": "A Great Map",
        "views": {("month", "=", "january"): "<div>Map jan</div>"},
    }
    widget1_view2 = {
        "widget_type": "map",
        "title": "A Great Map",
        "views": {("month", "=", "february"): "<div>Map feb</div>"},
    }
    widget2_view1 = {
        "widget_type": "plot",
        "title": "Super Cool Plot",
        "views": {("month", "=", "january"): "<div>Plot jan</div>"},
    }
    widget2_view2 = {
        "widget_type": "plot",
        "title": "Super Cool Plot",
        "views": {("month", "=", "february"): "<div>Plot feb</div>"},
    }
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
