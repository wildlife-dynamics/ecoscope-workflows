from datetime import datetime

import pytest
from ecoscope_workflows_core.tasks.filter._filter import TimeRange
from ecoscope_workflows_core.tasks.groupby._groupby import Grouper
from ecoscope_workflows_core.tasks.results import gather_dashboard
from ecoscope_workflows_core.tasks.results._dashboard import (
    Dashboard,
    EmumeratedWidgetSingleView,
)
from ecoscope_workflows_core.tasks.results._widget_types import GroupedWidget

DashboardFixture = tuple[list[GroupedWidget], Dashboard]


def assert_dashboards_equal(d1: Dashboard, d2: Dashboard):
    assert d1.grouper_choices
    assert d2.grouper_choices
    assert d1.grouper_choices.keys() == d2.grouper_choices.keys()
    # Does it matter if the order of the grouper values is different?
    assert (
        list(d1.grouper_choices.values()).sort()
        == list(d2.grouper_choices.values()).sort()
    )
    assert d1.keys == d2.keys
    assert d1.widgets == d2.widgets


@pytest.fixture
def single_filter_dashboard() -> DashboardFixture:
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/map.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/map.html",
        },
    )
    cool_plot = GroupedWidget(
        widget_type="graph",
        title="A Cool Plot",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/plot.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/plot.html",
        },
    )
    widgets = [great_map, cool_plot]
    dashboard = Dashboard(
        grouper_choices={Grouper(index_name="month"): ["january", "february"]},
        keys=[
            (("month", "=", "january"),),
            (("month", "=", "february"),),
        ],
        widgets=[great_map, cool_plot],
    )
    return widgets, dashboard


def test_gather_dashboard(single_filter_dashboard: DashboardFixture):
    grouped_widgets, expected_dashboard = single_filter_dashboard
    dashboard: Dashboard = gather_dashboard(
        title="A Great Dashboard",
        description="A dashboard with a map and a plot",
        time_range=TimeRange(
            since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
            until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        ),
        widgets=grouped_widgets,
        groupers=[Grouper(index_name="month")],
    )
    assert_dashboards_equal(dashboard, expected_dashboard)


def test__get_view(single_filter_dashboard: DashboardFixture):
    _, dashboard = single_filter_dashboard
    assert dashboard._get_view((("month", "=", "january"),)) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/jan/map.html",
        ),
        EmumeratedWidgetSingleView(
            id=1,
            widget_type="graph",
            title="A Cool Plot",
            data="/path/to/precomputed/jan/plot.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "february"),)) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/feb/map.html",
        ),
        EmumeratedWidgetSingleView(
            id=1,
            widget_type="graph",
            title="A Cool Plot",
            data="/path/to/precomputed/feb/plot.html",
        ),
    ]


def test_model_dump_views(single_filter_dashboard: DashboardFixture):
    _, dashboard = single_filter_dashboard
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
                "widget_type": "graph",
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
                "widget_type": "graph",
                "title": "A Cool Plot",
                "data": "/path/to/precomputed/feb/plot.html",
            },
        ],
    }


def test_model_dump_filters(single_filter_dashboard: DashboardFixture):
    _, dashboard = single_filter_dashboard
    assert dashboard.model_dump()["filters"] == {
        "schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "oneOf": [
                        {"const": "january", "title": "January"},
                        {"const": "february", "title": "February"},
                    ],
                    "default": "january",
                },
            },
            "uiSchema": {
                "month": {
                    "ui:title": "Month",
                    "ui:widget": "select",
                },
            },
        }
    }


@pytest.fixture
def two_filter_dashboard() -> DashboardFixture:
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
    widgets = [great_map]
    dashboard = Dashboard(
        grouper_choices={
            Grouper(index_name="month"): ["jan"],
            Grouper(index_name="year"): ["2022", "2023"],
        },
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022")),
            (("month", "=", "jan"), ("year", "=", "2023")),
        ],
        widgets=widgets,
    )
    return widgets, dashboard


def test_gather_dashboard_two_filter(two_filter_dashboard: DashboardFixture):
    grouped_widgets, expected_dashboard = two_filter_dashboard
    dashboard: Dashboard = gather_dashboard(
        title="A Great Dashboard",
        description="A dashboard with a map",
        time_range=TimeRange(
            since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
            until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        ),
        widgets=grouped_widgets,
        groupers=[Grouper(index_name="month"), Grouper(index_name="year")],
    )
    assert_dashboards_equal(dashboard, expected_dashboard)


def test__get_view_two_part_key(two_filter_dashboard: DashboardFixture):
    _, dashboard = two_filter_dashboard
    assert dashboard._get_view((("month", "=", "jan"), ("year", "=", "2022"))) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/map.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "jan"), ("year", "=", "2023"))) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2023/map.html",
        ),
    ]


def test_model_dump_views_two_filter(two_filter_dashboard: DashboardFixture):
    _, dashboard = two_filter_dashboard
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


def test_model_dump_filters_two_filter(two_filter_dashboard: DashboardFixture):
    _, dashboard = two_filter_dashboard
    assert dashboard.model_dump()["filters"] == {
        "schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "oneOf": [
                        {"const": "jan", "title": "Jan"},
                    ],
                    "default": "jan",
                },
                "year": {
                    "type": "string",
                    "oneOf": [
                        {"const": "2022", "title": "2022"},
                        {"const": "2023", "title": "2023"},
                    ],
                    "default": "2022",
                },
            },
            "uiSchema": {
                "month": {
                    "ui:title": "Month",
                    "ui:widget": "select",
                },
                "year": {
                    "ui:title": "Year",
                    "ui:widget": "select",
                },
            },
        }
    }


@pytest.fixture
def three_filter_dashboard() -> DashboardFixture:
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
    widgets = [great_map]
    dashboard = Dashboard(
        grouper_choices={
            Grouper(index_name="month"): ["jan"],
            Grouper(index_name="year"): ["2022"],
            Grouper(index_name="subject_name"): ["jo", "zo"],
        },
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "jo")),
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "zo")),
        ],
        widgets=widgets,
    )
    return widgets, dashboard


def test_gather_dashboard_three_filter(three_filter_dashboard: DashboardFixture):
    grouped_widgets, expected_dashboard = three_filter_dashboard
    dashboard: Dashboard = gather_dashboard(
        title="A Great Dashboard",
        description="A dashboard with a map",
        time_range=TimeRange(
            since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
            until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        ),
        widgets=grouped_widgets,
        groupers=[
            Grouper(index_name="month"),
            Grouper(index_name="year"),
            Grouper(index_name="subject_name"),
        ],
    )
    assert_dashboards_equal(dashboard, expected_dashboard)


def test__get_view_three_part_key(three_filter_dashboard: DashboardFixture):
    _, dashboard = three_filter_dashboard
    assert dashboard._get_view(
        (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "jo"))
    ) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/jo/map.html",
        ),
    ]
    assert dashboard._get_view(
        (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "zo"))
    ) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/jan/2022/zo/map.html",
        ),
    ]


def test_model_dump_views_three_filter(three_filter_dashboard: DashboardFixture):
    _, dashboard = three_filter_dashboard
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


def test_model_dump_filters_three_filter(three_filter_dashboard: DashboardFixture):
    _, dashboard = three_filter_dashboard
    assert dashboard.model_dump()["filters"] == {
        "schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "oneOf": [
                        {"const": "jan", "title": "Jan"},
                    ],
                    "default": "jan",
                },
                "year": {
                    "type": "string",
                    "oneOf": [
                        {"const": "2022", "title": "2022"},
                    ],
                    "default": "2022",
                },
                "subject_name": {
                    "type": "string",
                    "oneOf": [
                        {"const": "jo", "title": "Jo"},
                        {"const": "zo", "title": "Zo"},
                    ],
                    "default": "jo",
                },
            },
            "uiSchema": {
                "month": {
                    "ui:title": "Month",
                    "ui:widget": "select",
                },
                "year": {
                    "ui:title": "Year",
                    "ui:widget": "select",
                },
                "subject_name": {
                    "ui:title": "Subject Name",
                    "ui:widget": "select",
                },
            },
        }
    }


@pytest.fixture
def dashboard_with_none_views() -> DashboardFixture:
    great_map = GroupedWidget(
        widget_type="map",
        title="A Great Map",
        views={
            (("month", "=", "january"),): "/path/to/precomputed/jan/map.html",
            (("month", "=", "february"),): "/path/to/precomputed/feb/map.html",
        },
    )
    none_view_plot = GroupedWidget(
        widget_type="graph",
        title="A plot with only one view and no groupers",
        views={
            None: "/path/to/precomputed/single/plot.html",
        },
    )
    widgets = [great_map, none_view_plot]
    dashboard = Dashboard(
        grouper_choices={Grouper(index_name="month"): ["january", "february"]},
        keys=[
            (("month", "=", "january"),),
            (("month", "=", "february"),),
        ],
        widgets=widgets,
    )
    return widgets, dashboard


def test_gather_dashboard_with_none_views(dashboard_with_none_views: DashboardFixture):
    grouped_widgets, expected_dashboard = dashboard_with_none_views
    dashboard: Dashboard = gather_dashboard(
        title="A Great Dashboard",
        description="A dashboard with a map and a plot",
        time_range=TimeRange(
            since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
            until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
        ),
        widgets=grouped_widgets,
        groupers=[Grouper(index_name="month")],
    )
    assert_dashboards_equal(dashboard, expected_dashboard)


def test__get_view_with_none_views(dashboard_with_none_views: DashboardFixture):
    _, dashboard = dashboard_with_none_views
    assert dashboard._get_view((("month", "=", "january"),)) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/jan/map.html",
        ),
        EmumeratedWidgetSingleView(
            id=1,
            widget_type="graph",
            title="A plot with only one view and no groupers",
            data="/path/to/precomputed/single/plot.html",
        ),
    ]
    assert dashboard._get_view((("month", "=", "february"),)) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A Great Map",
            data="/path/to/precomputed/feb/map.html",
        ),
        EmumeratedWidgetSingleView(
            id=1,
            widget_type="graph",
            title="A plot with only one view and no groupers",
            data="/path/to/precomputed/single/plot.html",
        ),
    ]


def test_model_dump_views_with_none_views(dashboard_with_none_views: DashboardFixture):
    _, dashboard = dashboard_with_none_views
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
                "widget_type": "graph",
                "title": "A plot with only one view and no groupers",
                "data": "/path/to/precomputed/single/plot.html",
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
                "widget_type": "graph",
                "title": "A plot with only one view and no groupers",
                "data": "/path/to/precomputed/single/plot.html",
            },
        ],
    }


def test_model_dump_filters_with_none_views(
    dashboard_with_none_views: DashboardFixture,
):
    _, dashboard = dashboard_with_none_views
    assert dashboard.model_dump()["filters"] == {
        "schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "oneOf": [
                        {"const": "january", "title": "January"},
                        {"const": "february", "title": "February"},
                    ],
                    "default": "january",
                },
            },
            "uiSchema": {
                "month": {
                    "ui:title": "Month",
                    "ui:widget": "select",
                },
            },
        }
    }


@pytest.fixture
def dashboard_with_all_none_views() -> DashboardFixture:
    none_view_map = GroupedWidget(
        widget_type="map",
        title="A map with only one view and no groupers",
        views={
            None: "/path/to/precomputed/single/map.html",
        },
    )
    none_view_plot = GroupedWidget(
        widget_type="graph",
        title="A plot with only one view and no groupers",
        views={
            None: "/path/to/precomputed/single/plot.html",
        },
    )
    widgets = [none_view_map, none_view_plot]
    dashboard = Dashboard(widgets=widgets)
    return widgets, dashboard


def test_gather_dashboard_with_all_none_views(
    dashboard_with_all_none_views: DashboardFixture,
):
    grouped_widgets, expected_dashboard = dashboard_with_all_none_views
    dashboard: Dashboard = gather_dashboard(
        title=expected_dashboard.metadata.title,
        description=expected_dashboard.metadata.description,
        time_range=None,
        widgets=grouped_widgets,
        groupers=None,
    )
    # We don't need to use the custom `assert_dashboards_equal` function here
    # because there are no groupers or keys (with sorting concerns) to compare
    assert dashboard == expected_dashboard


def test__get_view_with_all_none_views(dashboard_with_all_none_views: DashboardFixture):
    _, dashboard = dashboard_with_all_none_views
    assert dashboard._get_view(None) == [
        EmumeratedWidgetSingleView(
            id=0,
            widget_type="map",
            title="A map with only one view and no groupers",
            data="/path/to/precomputed/single/map.html",
        ),
        EmumeratedWidgetSingleView(
            id=1,
            widget_type="graph",
            title="A plot with only one view and no groupers",
            data="/path/to/precomputed/single/plot.html",
        ),
    ]


def test_model_dump_views_with_all_none_views(
    dashboard_with_all_none_views: DashboardFixture,
):
    _, dashboard = dashboard_with_all_none_views
    assert dashboard.model_dump()["views"] == {
        "{}": [
            {
                "id": 0,
                "widget_type": "map",
                "title": "A map with only one view and no groupers",
                "data": "/path/to/precomputed/single/map.html",
            },
            {
                "id": 1,
                "widget_type": "graph",
                "title": "A plot with only one view and no groupers",
                "data": "/path/to/precomputed/single/plot.html",
            },
        ],
    }


def test_model_dump_filters_with_all_none_views(
    dashboard_with_all_none_views: DashboardFixture,
):
    _, dashboard = dashboard_with_all_none_views
    assert dashboard.model_dump()["filters"] is None
