from ecoscope_workflows.tasks.results._dashboard import Dashboard, EmumeratedWidgetView
from ecoscope_workflows.tasks.results._widget_types import GroupedWidget


def test__get_view():
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


def test__get_view_two_part_key():
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
    dashboard = Dashboard(
        groupers={"month": ["jan"], "year": ["2022", "2023"]},
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022")),
            (("month", "=", "jan"), ("year", "=", "2023")),
        ],
        widgets=[great_map],
    )
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


def test__get_view_three_part_key():
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
    dashboard = Dashboard(
        groupers={"month": ["jan"], "year": ["2022"], "subject_name": ["jo", "zo"]},
        keys=[
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "jo")),
            (("month", "=", "jan"), ("year", "=", "2022"), ("subject_name", "=", "zo")),
        ],
        widgets=[great_map],
    )
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
