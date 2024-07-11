import json
from typing import Annotated, Any, Generator, TypedDict
from dataclasses import dataclass

from pydantic import BaseModel, Field, model_serializer

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter

WidgetData = str  # FIXME: structured widget data, not just a string?


@dataclass
class WidgetBase:
    widget_type: str
    title: str


@dataclass
class Widget(WidgetBase):
    id: int
    data: WidgetData


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


class GroupedWidgetDict(TypedDict):
    widget_type: str
    title: str
    views: dict[CompositeFilter, WidgetData]


def can_merge(w1: GroupedWidgetDict, w2: GroupedWidgetDict):
    return w1["widget_type"] == w2["widget_type"] and w1["title"] == w2["title"]


def merge_views(w1: GroupedWidgetDict, w2: GroupedWidgetDict):
    merged_views = w1["views"].copy()
    merged_views.update(w2["views"])  # allows overwriting but that should be ok?
    return merged_views


def merge_widgets(widgets: list[GroupedWidgetDict]) -> list[GroupedWidgetDict]:
    merged = {}
    for w in widgets:
        key = (w["widget_type"], w["title"])
        if key not in merged:
            merged[key] = w.copy()
        else:
            merged[key]["views"] = merge_views(merged[key], w)
    return list(merged.values())


GrouperName = str
GrouperChoices = list[str]


def composite_filters_to_grouper_choices_dict(
    keys: list[CompositeFilter],
) -> dict[GrouperName, GrouperChoices]:
    """Converts a list of composite filters to a dict of grouper choices.
    For example:
    ```
    [
        (('animal_name', '=', 'Ao'), ('month', '=', 'February')),
        (('animal_name', '=', 'Ao'), ('month', '=', 'January')),
        (('animal_name', '=', 'Bo'), ('month', '=', 'February')),
        (('animal_name', '=', 'Bo'), ('month', '=', 'January')),
    ]
    ```
    Becomes:
    ```
    {'animal_name': ['Ao', 'Bo'], 'month': ['February', 'January']}
    ```
    """
    choices: dict[GrouperName, GrouperChoices] = {}
    for k in keys:
        for filter, _, value in k:
            if filter not in choices:
                choices[filter] = []
            if value not in choices[filter]:
                choices[filter].append(value)

    for filter in choices:
        # TODO: sort by logical order for the type of grouper (e.g. month names, not alphabetically)
        choices[filter].sort()

    return choices


@dataclass
class Metadata:
    title: str
    description: str


class Dashboard(BaseModel):
    groupers: dict[GrouperName, GrouperChoices]
    keys: list[CompositeFilter]
    widgets: list[GroupedWidget]
    metadata: Metadata = Field(default_factory=dict)

    def _get_view(self, key: CompositeFilter) -> list[Widget]:
        # TODO: ungrouped widgets
        return [w.get_view(key, id=i) for i, w in enumerate(self.widgets) if key in w.views]

    def _iter_views(
        self,
    ) -> Generator[tuple[CompositeFilter, list[Widget]], None, None]:
        for k in self.keys:
            yield k, self._get_view(k)

    def _iter_views_json(self) -> Generator[tuple[str, list[Widget]], None, None]:
        for k in self.keys:
            asdict = {attr: value for attr, _, value in k}
            yield json.dumps(asdict, sort_keys=True), self._get_view(k)

    @property
    def views(self) -> dict[CompositeFilter, list[Widget]]:
        return {k: v for k, v in self._iter_views()}

    @property
    def views_json(self) -> dict[str, list[Widget]]:
        return {k: v for k, v in self._iter_views_json()}
    
    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "filters": self.groupers,
            "views": self.views_json,
            "metadata": self.metadata,
        }


@distributed
def gather_dashboard(
    widgets: Annotated[list[dict], Field()],
    groupers: Annotated[list, Field()],
):
    grouped_widgets = [GroupedWidget(**w) for w in widgets]
    keys = list(grouped_widgets[0].views)
    # TODO: ungrouped widgets (i think this would be just (None, None) keys or something)
    assert all(
        keys == list(w.views) for w in grouped_widgets
    ), "All widgets must have the same keys"
    grouper_choices = composite_filters_to_grouper_choices_dict(keys)
    # make sure we didn't lose track of any groupers inflight
    print("Checking equality of: ", set(groupers), set(grouper_choices.keys()))
    assert set(groupers) == set(
        list(grouper_choices.keys())
    ), "All groupers must be present in the keys"
    return Dashboard(groupers=grouper_choices, keys=keys, widgets=grouped_widgets)
