from typing import TypeAlias, Literal
from dataclasses import dataclass
from pathlib import Path

from pydantic_core import Url

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
    data: WidgetData
    view: CompositeFilter | None = None


@dataclass
class GroupedWidget(WidgetBase):
    views: dict[CompositeFilter | None, WidgetData]

    def get_view(self, view: CompositeFilter) -> WidgetSingleView:
        """Get the view for a specific CompositeFilter. If the widget has only
        a single (ungrouped) view, then that single view is returned regardless
        of which `view` is requested.
        """
        _view = view if not list(self.views) == [None] else None
        return WidgetSingleView(
            widget_type=self.widget_type,
            title=self.title,
            view=view,
            data=self.views[_view],
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