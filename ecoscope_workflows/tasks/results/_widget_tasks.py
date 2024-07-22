from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter
from ecoscope_workflows.tasks.results._widget_types import (
    GroupedWidget,
    PrecomputedHTMLWidgetData,
    TextWidgetData,
    WidgetSingleView,
)


@distributed
def create_map_widget_single_view(
    title: Annotated[str, Field(description="The title of the widget")],
    data: Annotated[
        PrecomputedHTMLWidgetData, Field(description="Path to precomputed HTML")
    ],
    view: Annotated[
        CompositeFilter | None, Field(description="If grouped, the view of the widget")
    ] = None,
) -> Annotated[WidgetSingleView, Field(description="The widget")]:
    from ecoscope_workflows.tasks.results._widget_types import WidgetSingleView

    return WidgetSingleView(
        widget_type="map",
        title=title,
        view=view,
        data=data,
    )


@distributed
def create_plot_widget_single_view(
    title: Annotated[str, Field(description="The title of the widget")],
    data: Annotated[
        PrecomputedHTMLWidgetData, Field(description="Path to precomputed HTML")
    ],
    view: Annotated[
        CompositeFilter | None, Field(description="If grouped, the view of the widget")
    ] = None,
) -> Annotated[WidgetSingleView, Field(description="The widget")]:
    from ecoscope_workflows.tasks.results._widget_types import WidgetSingleView

    return WidgetSingleView(
        widget_type="plot",
        title=title,
        view=view,
        data=data,
    )


@distributed
def create_text_widget_single_view(
    title: Annotated[str, Field(description="The title of the widget")],
    data: Annotated[TextWidgetData, Field(description="Text to display.")],
    view: Annotated[
        CompositeFilter | None, Field(description="If grouped, the view of the widget")
    ] = None,
) -> Annotated[WidgetSingleView, Field(description="The widget")]:
    from ecoscope_workflows.tasks.results._widget_types import WidgetSingleView

    return WidgetSingleView(
        widget_type="text",
        title=title,
        view=view,
        data=data,
    )


@distributed
def create_single_value_widget_single_view(
    title: Annotated[str, Field(description="The title of the widget")],
    data: Annotated[
        PrecomputedHTMLWidgetData, Field(description="Path to precomputed HTML")
    ],
    view: Annotated[
        CompositeFilter | None, Field(description="If grouped, the view of the widget")
    ] = None,
) -> Annotated[WidgetSingleView, Field(description="The widget")]:
    from ecoscope_workflows.tasks.results._widget_types import WidgetSingleView

    return WidgetSingleView(
        widget_type="single_value",
        title=title,
        view=view,
        data=data,
    )


@distributed
def merge_widget_views(
    widgets: Annotated[list[WidgetSingleView], Field()],
) -> Annotated[list[GroupedWidget], Field(description="The merged widgets")]:
    from ecoscope_workflows.tasks.results._widget_types import GroupedWidget

    as_grouped_widgets = [
        GroupedWidget(
            widget_type=w.widget_type,
            title=w.title,
            views={w.view: w.data},
        )
        for w in widgets
    ]
    merged: dict[tuple[str, str], GroupedWidget] = {}
    for gw in as_grouped_widgets:
        if gw.merge_key not in merged:
            merged[gw.merge_key] = gw
        else:
            merged[gw.merge_key] |= gw
    return list(merged.values())
