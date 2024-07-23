from ecoscope_workflows.tasks.results._dashboard import Dashboard, EmumeratedWidgetView
from ecoscope_workflows.tasks.results._widget_types import GroupedWidget


def test_dashboard__get_view():
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
    dashboard = Dashboard(
        groupers={"month": ["january", "february"]},
        keys=[
            (("month", "=", "january"),),
            (("month", "=", "february"),),
        ],
        widgets=[great_map, cool_plot],
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
            title="A Cool Plot",
            data="/path/to/precomputed/jan/plot.html",
        ),
    ]
    # assert dashboard._get_view([("a", "a2")]) == [
    #     EmumeratedWidget(id=2, widget_type="GroupedWidget", title="a2", data=WidgetData()),
    # ]
    # assert dashboard._get_view([("b", "b2")]) == [
    #     EmumeratedWidget(id=3, widget_type="GroupedWidget", title="b2", data=WidgetData()),
    # ]
