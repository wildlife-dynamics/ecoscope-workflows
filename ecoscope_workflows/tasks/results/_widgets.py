from typing import Annotated, TypeAlias, Literal
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field
from pydantic_core import Url

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter

WidgetTypes = Literal["plot", "map", "text", "single_value"]

PrecomputedHTMLWidgetData: TypeAlias = Path | Url
TextWidgetData: TypeAlias = str
SingleValueWidgetData: TypeAlias = int | float

WidgetData: TypeAlias = (
    PrecomputedHTMLWidgetData | TextWidgetData | SingleValueWidgetData
)


@dataclass
class WidgetBase:
    widget_type: WidgetTypes
    title: str


@dataclass
class WidgetSingleView(WidgetBase):
    view: CompositeFilter
    data: WidgetData


@dataclass
class GroupedWidget(WidgetBase):
    views: dict[CompositeFilter, WidgetData]

    def get_view(self, view: CompositeFilter) -> WidgetSingleView:
        return WidgetSingleView(
            widget_type=self.widget_type,
            title=self.title,
            view=view,
            data=self.views[view],
        )

    @property
    def merge_key(self):
        """If two GroupedWidgets have the same merge key, they can be merged."""
        return (self.widget_type, self.title)

    def __ior__(self, other: "GroupedWidget"):
        """Implements the in-place or operator, i.e. `|=`, used to merge two GroupedWidgets."""
        if self.merge_key != other.merge_key:
            raise ValueError(
                "Cannot merge GroupedWidgets with different merge keys: "
                f"{self.merge_key} != {other.merge_key}"
            )
        self.views.update(other.views)
        return self


@distributed
def create_map_widget_single_view(
    title: Annotated[str, Field(description="The title of the widget")],
    data: Annotated[
        PrecomputedHTMLWidgetData, Field(description="Path to precomputed HTML")
    ],
    view: Annotated[
        CompositeFilter, Field(description="If grouped, the view of the widget")
    ],
) -> WidgetSingleView:
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
        CompositeFilter, Field(description="If grouped, the view of the widget")
    ],
) -> WidgetSingleView:
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
        CompositeFilter, Field(description="If grouped, the view of the widget")
    ],
) -> WidgetSingleView:
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
        CompositeFilter, Field(description="If grouped, the view of the widget")
    ],
) -> WidgetSingleView:
    return WidgetSingleView(
        widget_type="single_value",
        title=title,
        view=view,
        data=data,
    )


@distributed
def merge_widget_views(
    widgets: Annotated[list[WidgetSingleView], Field()],
) -> list[GroupedWidget]:
    # cast all WidgetSingleViews to GroupedWidgets with a single view,
    # which makes merging easier
    _widgets = [
        GroupedWidget(
            widget_type=w.widget_type,
            title=w.title,
            views={w.view: w.data},
        )
        for w in widgets
    ]
    # then merge all views with the same merge key
    merged: dict[tuple[str, str], GroupedWidget] = {}
    for w in _widgets:
        if w.merge_key not in merged:
            merged[w.merge_key] = w
        else:
            merged[w.merge_key] |= w
    return list(merged.values())
