from typing import Annotated, TypeAlias, TypedDict, Literal
from dataclasses import dataclass

from pydantic import Field, HttpUrl

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter

WidgetData: TypeAlias = HttpUrl | str | int  # any other types?


@dataclass
class WidgetBase:
    widget_type: str
    title: str


@dataclass
class Widget(WidgetBase):
    id: int
    data: WidgetData


class GroupedWidgetDict(TypedDict):
    widget_type: str
    title: str
    views: dict[CompositeFilter, WidgetData]


WidgetTypes = Literal["plot", "map", "text", "single_value"]


@distributed
def create_widget_single_view(
    widget_type: Annotated[WidgetTypes, Field(description="The type of widget.")],
    title: str,
    view: CompositeFilter,
    data: str,
) -> Annotated[GroupedWidgetDict, Field()]:
    return {
        "widget_type": widget_type,
        "title": title,
        "views": {view: data},
    }


def _merge_views(w1: GroupedWidgetDict, w2: GroupedWidgetDict):
    merged_views = w1["views"].copy()
    merged_views.update(w2["views"])  # allows overwriting but that should be ok?
    return merged_views


@dataclass
class GroupedWidget(WidgetBase):
    views: dict[CompositeFilter, WidgetData]

    def get_view(self, key: CompositeFilter, id: int) -> Widget:
        return Widget(
            id=id,
            widget_type=self.widget_type,
            title=self.title,
            data=self.views[key],
        )


@distributed
def merge_widgets(
    widgets: Annotated[list[GroupedWidgetDict], Field()],
) -> list[GroupedWidget]:
    merged = {}
    for w in widgets:
        key = (w["widget_type"], w["title"])
        if key not in merged:
            merged[key] = w.copy()
        else:
            merged[key]["views"] = _merge_views(merged[key], w)
    return [GroupedWidget(**w) for w in list(merged.values())]
