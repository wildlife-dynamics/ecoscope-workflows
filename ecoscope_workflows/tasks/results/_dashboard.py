import json
from dataclasses import dataclass
from typing import Annotated, Any, Generator

from pydantic import BaseModel, Field, model_serializer

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import (
    CompositeFilter,
    IndexName,
    IndexValue,
)
from ecoscope_workflows.tasks.results._widget_types import (
    GroupedWidget,
    WidgetData,
    WidgetSingleView,
)


@dataclass
class EmumeratedWidgetView:
    """A widget view with an enumerated integer `id` for use in a dashboard.
    Dashboards require a unique integer identifier for each widget, to affiliate
    layout information with the widget. Unlike a `WidgetSingleView`, this class
    does not contain a `view` field because the dashboard is responsible for
    knowing which view to display.
    """

    id: int
    widget_type: str
    title: str
    data: WidgetData

    @classmethod
    def from_single_view(cls, id: int, view: WidgetSingleView):
        return cls(
            id=id,
            widget_type=view.widget_type,
            title=view.title,
            data=view.data,
        )


@dataclass
class Metadata:
    """Descriptive metadata for the dashboard."""

    title: str = ""
    description: str = ""


class Dashboard(BaseModel):
    groupers: dict[IndexName, list[IndexValue]]
    keys: list[CompositeFilter]
    widgets: list[GroupedWidget]
    metadata: Metadata = Field(default_factory=Metadata)

    def _get_view(self, view: CompositeFilter) -> list[EmumeratedWidgetView]:
        # TODO: ungrouped widgets
        return [
            EmumeratedWidgetView.from_single_view(id=i, view=w.get_view(view))
            for i, w in enumerate(self.widgets)
        ]

    def _iter_views_json(
        self,
    ) -> Generator[tuple[str, list[EmumeratedWidgetView]], None, None]:
        for k in self.keys:
            asdict = {attr: value for attr, _, value in k}
            yield json.dumps(asdict, sort_keys=True), self._get_view(k)

    @property
    def views_json(self) -> dict[str, list[EmumeratedWidgetView]]:
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
) -> dict[IndexName, list[IndexValue]]:
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
    choices: dict[IndexName, list[IndexValue]] = {}
    for k in keys:
        if k is not None:
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
    grouped_widgets: Annotated[list[GroupedWidget], Field()],
    groupers: Annotated[list, Field()],
):
    keys = list(grouped_widgets[0].views)
    assert all(
        keys == list(w.views) for w in grouped_widgets
    ), (
        "All widgets must have the same keys"
    )  # FIXME: This isn't true for ungrouped widgets
    grouper_choices = composite_filters_to_grouper_choices_dict(keys)
    # make sure we didn't lose track of any groupers inflight
    assert set(groupers) == set(
        list(grouper_choices.keys())
    ), "All groupers must be present in the keys"
    return Dashboard(groupers=grouper_choices, keys=keys, widgets=grouped_widgets)
