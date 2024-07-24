import json
from dataclasses import dataclass
from typing import Annotated, Any, Generator

from pydantic import BaseModel, Field, model_serializer

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.jsonschema import (
    ReactJSONSchemaFormFilters,
    RJSFFilter,
    RJSFFilterProperty,
    RJSFFilterUiSchema,
)
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
    """A dashboard composed of grouped widgets. Widgets without groupers are
    represented by a single view with a `None` key. See `GroupedWidget` for more.

    Args:
        widgets: A list of grouped widgets.
        groupers: A dictionary of groupers and their possible values.
            If all widgets are ungrouped, this field is `None`.
        keys: A list of composite filters that represent the possible views for the grouped widgets.
            If all widgets are ungrouped, this field is `None`.
        metadata: Descriptive metadata for the dashboard.
    """

    widgets: list[GroupedWidget]
    groupers: dict[IndexName, list[IndexValue]] | None = None
    keys: list[CompositeFilter] | None = None
    metadata: Metadata = Field(default_factory=Metadata)

    def _get_view(self, view: CompositeFilter | None) -> list[EmumeratedWidgetView]:
        return [
            EmumeratedWidgetView.from_single_view(id=i, view=w.get_view(view))
            for i, w in enumerate(self.widgets)
        ]

    def _iter_views_json(
        self,
    ) -> Generator[tuple[str, list[EmumeratedWidgetView]], None, None]:
        if not self.keys:
            # if there is no grouping for any widgets, there is only one view
            # so yield it back as a single view with an empty key
            yield json.dumps({}), self._get_view(None)
            # and then stop iterating
            return
        for k in self.keys:
            asdict = {attr: value for attr, _, value in k}
            yield json.dumps(asdict, sort_keys=True), self._get_view(k)

    @property
    def views_json(self) -> dict[str, list[EmumeratedWidgetView]]:
        return {k: v for k, v in self._iter_views_json()}

    @property
    def rjsf_filters_json(self) -> ReactJSONSchemaFormFilters | None:
        return (
            ReactJSONSchemaFormFilters(
                options={
                    grouper_name: RJSFFilter(
                        property=RJSFFilterProperty(
                            type="string",
                            enum=grouper_choices,
                            enumNames=[choice.title() for choice in grouper_choices],
                            default=grouper_choices[0],
                        ),
                        uiSchema=RJSFFilterUiSchema(
                            title=grouper_name.title().replace("_", " "),
                            # TODO: allow specifying help text
                            # _help=f"Select a {grouper_name} to filter by.",
                        ),
                    )
                    for grouper_name, grouper_choices in self.groupers.items()
                }
            ).model_dump()
            if self.groupers is not None
            else None
        )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {
            "filters": self.rjsf_filters_json,
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
    title: Annotated[str, Field(description="The title of the dashboard")],
    description: Annotated[str, Field(description="The description of the dashboard")],
    widgets: Annotated[
        list[GroupedWidget] | WidgetSingleView,
        Field(
            description="""\
            A list of grouped widgets (for a dashboard with multiple widgets),
            or a single grouped widget (for a dashboard with a single widget).
            """,
        ),
    ],
    groupers: Annotated[
        list | None,
        Field(
            description="""\
            A list of groupers that are used to group the widgets.
            If all widgets are ungrouped, this field is `None`.
            """
        ),
    ],
) -> Annotated[Dashboard, Field()]:
    grouped_widgets = (
        [GroupedWidget.from_single_view(widgets)]
        if isinstance(widgets, WidgetSingleView)
        else widgets
    )
    if groupers:
        for gw in grouped_widgets:
            keys_sample = list(gw.views)
            if keys_sample != [None]:
                # we want to get a representative set of keys for the grouped
                # widgets, so we break after the first one that has keys. This
                # logic prevents the case where the first widget(s) in the list
                # are ungrouped and their keys are thus not representative.
                break
        for gw in grouped_widgets:
            if list(gw.views) != [None]:
                # now make sure all grouped widgets have the same keys.
                assert (
                    list(gw.views) == keys_sample
                ), "All grouped widgets must have the same keys"
        grouper_choices = composite_filters_to_grouper_choices_dict(keys_sample)
        # make sure we didn't lose track of any groupers inflight
        assert set(groupers) == set(
            list(grouper_choices.keys())
        ), "All groupers must be present in the keys"
    return Dashboard(
        widgets=grouped_widgets,
        groupers=(grouper_choices if groupers else None),
        keys=(keys_sample if groupers else None),
        metadata=Metadata(title=title, description=description),
    )
