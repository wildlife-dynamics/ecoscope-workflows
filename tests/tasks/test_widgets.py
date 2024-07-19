from ecoscope_workflows.tasks.results import create_widget_single_view


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
