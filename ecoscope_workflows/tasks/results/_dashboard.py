import json
from dataclasses import asdict, dataclass
from typing import Annotated, Any, Generator, TypeAlias

from pydantic import BaseModel, Field, model_serializer

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import CompositeFilter
from ecoscope_workflows.tasks.results._widget_types import GroupedWidget, WidgetData

GrouperName: TypeAlias = str
GrouperChoices: TypeAlias = list[str]


@dataclass
class EmumeratedWidget:
    id: int
    widget_type: str
    title: str
    data: WidgetData


@dataclass
class Metadata:
    title: str = ""
    description: str = ""


class Dashboard(BaseModel):
    groupers: dict[GrouperName, GrouperChoices]
    keys: list[CompositeFilter]
    widgets: list[GroupedWidget]
    metadata: Metadata = Field(default_factory=Metadata)

    def _get_view(self, view: CompositeFilter) -> list[EmumeratedWidget]:
        # TODO: ungrouped widgets
        return [
            EmumeratedWidget(id=i, **asdict(w.get_view(view)))
            for i, w in enumerate(self.widgets)
            if view in w.views
        ]

    def _iter_views(
        self,
    ) -> Generator[tuple[CompositeFilter, list[EmumeratedWidget]], None, None]:
        for k in self.keys:
            yield k, self._get_view(k)

    def _iter_views_json(
        self,
    ) -> Generator[tuple[str, list[EmumeratedWidget]], None, None]:
        for k in self.keys:
            asdict = {attr: value for attr, _, value in k}
            yield json.dumps(asdict, sort_keys=True), self._get_view(k)

    @property
    def views(self) -> dict[CompositeFilter, list[EmumeratedWidget]]:
        return {k: v for k, v in self._iter_views()}

    @property
    def views_json(self) -> dict[str, list[EmumeratedWidget]]:
        return {k: v for k, v in self._iter_views_json()}

    @property
    def filters_json(self):
        return [
            {
                "title": grouper_name.title().replace("_", " "),
                "key": grouper_name,
                "type": "select",  # FIXME: infer from type of values, or allow specifying
                "options": [
                    {"key": choice.title(), "value": choice}
                    for choice in grouper_choices
                ],
            }
            for grouper_name, grouper_choices in self.groupers.items()
        ]

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "filters": self.filters_json,
            "views": self.views_json,
            "metadata": self.metadata,
            "layout": [],  # this is a placeholder for future use by server
        }


def composite_filters_to_grouper_choices_dict(
    keys: list[CompositeFilter | None],
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
    assert set(groupers) == set(
        list(grouper_choices.keys())
    ), "All groupers must be present in the keys"
    return Dashboard(groupers=grouper_choices, keys=keys, widgets=grouped_widgets)