import pytest

from ecoscope_workflows.tasks.results._dashboard import Dashboard, EmumeratedWidgetView
from ecoscope_workflows.tasks.results._widget_types import GroupedWidget


@pytest.fixture
def single_filter_dashboard():
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/map.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/map.html",
        },
    )
    cool_plot = GroupedWidget(
        widget_type="plot",
        title="A Cool Plot",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/plot.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/plot.html",
        },
    )
    return Dashboard(
        groupers={"month": ["january", "february"]},
        keys=[
            (("month", "=", "january"),),
            (("month", "=", "february"),),
        ],
        widgets=[great_map, cool_plot],
    )


def test__get_view(single_filter_dashboard: Dashboard):
    dashboard = single_filter_dashboard
    assert dashboard._get_view((("month", "=", "january"),)) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/jan/map.html",
        ),
        EmumeratedWidgetView(
            id=1,
            widget_type="plot",
            title="A Cool Plot",
            data="/path/to/precomputed/jan/plot.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "february"),)) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/feb/map.html",
        ),
        EmumeratedWidgetView(
            id=1,
            widget_type="plot",
            title="A Cool Plot",
            data="/path/to/precomputed/feb/plot.html",
        ),
    ]


def test_model_dump_views(single_filter_dashboard: Dashboard):
    dashboard = single_filter_dashboard
    assert dashboard.model_dump()["views"] == {
        '{"month": "january"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/precomputed/jan/map.html",
            },
            {
                "id": 1,
                "widget_type": "plot",
                "title": "A Cool Plot",
                "data": "/path/to/precomputed/jan/plot.html",
            },
        ],
        '{"month": "february"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/precomputed/feb/map.html",
            },
            {
                "id": 1,
                "widget_type": "plot",
                "title": "A Cool Plot",
                "data": "/path/to/precomputed/feb/plot.html",
            },
        ],
    }


@pytest.fixture
def two_filter_dashboard():
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (
                ("month", "=", "jan"),
                ("year", "=", "2022"),
            ): "/path/to/jan/2022/map.html",
            (
                ("month", "=", "jan"),
                ("year", "=", "2023"),
            ): "/path/to/jan/2023/map.html",
        },
    )
    return Dashboard(
        groupers={"month": ["jan"], "year": ["2022", "2023"]},
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022")),
            (("month", "=", "jan"), ("year", "=", "2023")),
        ],
        widgets=[great_map],
    )


def test__get_view_two_part_key(two_filter_dashboard: Dashboard):
    dashboard = two_filter_dashboard
    assert dashboard._get_view((("month", "=", "jan"), ("year", "=", "2022"))) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/map.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "jan"), ("year", "=", "2023"))) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2023/map.html",
        ),
    ]


def test_model_dump_views_two_filter(two_filter_dashboard: Dashboard):
    dashboard = two_filter_dashboard
    assert dashboard.model_dump()["views"] == {
        '{"month": "jan", "year": "2022"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/jan/2022/map.html",
            },
        ],
        '{"month": "jan", "year": "2023"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/jan/2023/map.html",
            },
        ],
    }


@pytest.fixture
def three_filter_dashboard():
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (
                ("month", "=", "jan"),
                ("year", "=", "2022"),
                ("subject_name", "=", "jo"),
            ): "/path/to/jan/2022/jo/map.html",
            (
                ("month", "=", "jan"),
                ("year", "=", "2022"),
                ("subject_name", "=", "zo"),
            ): "/path/to/jan/2022/zo/map.html",
        },
    )
    return Dashboard(
        groupers={"month": ["jan"], "year": ["2022"], "subject_name": ["jo", "zo"]},
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "jo")),
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "zo")),
        ],
        widgets=[great_map],
    )


def test__get_view_three_part_key(three_filter_dashboard: Dashboard):
    dashboard = three_filter_dashboard
    assert dashboard._get_view(
        (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "jo"))
    ) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/jo/map.html",
        ),
    ]
    assert dashboard._get_view(
        (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "zo"))
    ) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/zo/map.html",
        ),
    ]


def test_model_dump_views_three_filter(three_filter_dashboard: Dashboard):
    dashboard = three_filter_dashboard
    assert dashboard.model_dump()["views"] == {
        # Note sort_keys=True in `json.dumps` in _iter_views_json method of Dashboard
        # results in the json keys being ordered differently than the keys in the tuple
        '{"month": "jan", "subject_name": "jo", "year": "2022"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/jan/2022/jo/map.html",
            },
        ],
        '{"month": "jan", "subject_name": "zo", "year": "2022"}': [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A Great Map",
                "data": "/path/to/jan/2022/zo/map.html",
            },
        ],
    }


def test__get_view_with_none_views():
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/map.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/map.html",
        },
    )
    none_view_plot = GroupedWidget(
        widget_type="plot",
        title="A plot with only one view and no groupers",
        views={
            None: "/path/to/precomputed/single/plot.html",
        },
    )
    dashboard = Dashboard(
        groupers={"month": ["january", "february"]},
        keys=[
            (("month", "=", "january"),),
            (("month", "=", "february"),),
        ],
        widgets=[great_map, none_view_plot],
    )
    assert dashboard._get_view((("month", "=", "january"),)) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/jan/map.html",
        ),
        EmumeratedWidgetView(
            id=1,
            widget_type="plot",
            title="A plot with only one view and no groupers",
            data="/path/to/precomputed/single/plot.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "february"),)) == [
        EmumeratedWidgetView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/feb/map.html",
        ),
        EmumeratedWidgetView(
            id=1,
            widget_type="plot",
            title="A plot with only one view and no groupers",
            data="/path/to/precomputed/single/plot.html",
        ),
    ]
