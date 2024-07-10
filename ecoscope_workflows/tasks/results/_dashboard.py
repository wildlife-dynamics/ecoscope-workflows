from typing import Annotated, TypedDict
from dataclasses import dataclass

from pydantic import Field

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter


class Widget(TypedDict):
    widget_type: str
    views: dict[CompositeFilter, str]
    title: str


def can_merge(w1: Widget, w2: Widget):
    return w1["widget_type"] == w2["widget_type"] and w1["title"] == w2["title"]


def merge_views(w1: Widget, w2: Widget):
    merged_views = w1["views"].copy()
    merged_views.update(w2["views"])  # allows overwriting but that should be ok?
    return merged_views


def merge_widgets(widgets: list[Widget]) -> list[Widget]:
    merged = {}
    for w in widgets:
        key = (w["widget_type"], w["title"])
        if key not in merged:
            merged[key] = w.copy()
        else:
            merged[key]["views"] = merge_views(merged[key], w)
    return list(merged.values())


@dataclass
class Dashboard:
    groupers: list
    widgets: list[Widget]

    @property
    def views(self): ...


@distributed
def gather_dashboard(
    widgets: Annotated[list[Widget], Field()],
    groupers: Annotated[list, Field()],
):
    return Dashboard(groupers=groupers, widgets=widgets)
