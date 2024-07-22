from typing import Annotated, TypeAlias, TypedDict, Literal
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field
from pydantic_core import Url

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter

WidgetTypes = Literal["plot", "map", "text", "single_value"]
WidgetData: TypeAlias = Path | Url | str | int | float  # any other types?


WIDGET_TYPES_ALLOWABLE_DATA: dict[str, tuple] = {
    # if a plot or a map is a `str`, it's not intended to be a str of raw
    # html content, but rather a string that can be parsed to a Path or URL.
    # this would happen if we pass a str value and run the create widget task
    # _without_ validate=True, and therefore the value is not parsed.
    "plot": (str, Path, Url),
    "map": (str, Path, Url),
    "text": (str,),
    "single_value": (int, float),
}


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


@distributed
def create_widget_single_view(
    widget_type: Annotated[WidgetTypes, Field(description="The type of widget.")],
    title: str,
    view: CompositeFilter,
    data: WidgetData,
) -> Annotated[GroupedWidgetDict, Field()]:
    # maybe there's a way to express the relationships expressed by WIDGET_TYPES_ALLOWABLE_DATA
    # in the function signature directly? a BaseModel could do this easily, but in general I've
    # been trying to avoid nested arguments for clarity. but pushing this assert to the signature
    # would allow us to more easily do static checks on inputs, rather than failing at runtime if
    # there is a mismatch. for now this will do but this is somethign to keep in mind,
    assert isinstance(data, WIDGET_TYPES_ALLOWABLE_DATA[widget_type])
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
def merge_widget_views(
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
