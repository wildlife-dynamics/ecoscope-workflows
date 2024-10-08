import json
from dataclasses import dataclass
from typing import Annotated, Any, Generator

from pydantic import BaseModel, Field, model_serializer
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows_core.decorators import task
from ecoscope_workflows_core.indexes import CompositeFilter, IndexName, IndexValue
from ecoscope_workflows_core.jsonschema import (
    oneOf,
    ReactJSONSchemaFormFilters,
    RJSFFilter,
    RJSFFilterProperty,
    RJSFFilterUiSchema,
)
from ecoscope_workflows_core.tasks.groupby._groupby import Grouper
from ecoscope_workflows_core.tasks.results._widget_types import (
    GroupedWidget,
    WidgetBase,
    WidgetData,
    WidgetSingleView,
)


@dataclass
class EmumeratedWidgetSingleView(WidgetBase):
    """A widget view with an enumerated integer `id` for use in a dashboard.
    Dashboards require a unique integer identifier for each widget, to affiliate
    layout information with the widget. Unlike a `WidgetSingleView`, this class
    does not contain a `view` field because the dashboard is responsible for
    knowing which view to display.
    """

    id: int
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


class DashboardJson(BaseModel):
    """A JSON-serialized representation of a dashboard."""

    filters: dict | None
    views: dict[str, list[EmumeratedWidgetSingleView]]
    metadata: Metadata
    layout: list  # this is a placeholder for future use by server


class Dashboard(BaseModel):
    """A dashboard composed of grouped widgets. Widgets without groupers are
    represented by a single view with a `None` key. See `GroupedWidget` for more.

    Args:
        widgets: A list of grouped widgets.
        grouper_choices: A dictionary of groupers and their possible values.
            If all widgets are ungrouped, this field is `None`.
        keys: A list of composite filters that represent the possible views for the grouped widgets.
            If all widgets are ungrouped, this field is `None`.
        metadata: Descriptive metadata for the dashboard.
    """

    widgets: list[GroupedWidget]
    grouper_choices: dict[Grouper, list[IndexValue]] | None = None
    keys: list[CompositeFilter] | None = None
    metadata: Metadata = Field(default_factory=Metadata)

    def _get_view(
        self, view: CompositeFilter | None
    ) -> list[EmumeratedWidgetSingleView]:
        """Get the overal view for the dashboard, by fetching that view for each widget.
        and returning a list of `EmumeratedWidgetSingleView` instances for that view.
        If the dashboard contains a mix of grouped and ungrouped widgets, the ungrouped
        widgets will not have a view for the requested CompositeFilter, so in that case
        request `None` (i.e. the static view) for that widget, even if the requested view
        is a CompositeFilter.
        """
        return [
            EmumeratedWidgetSingleView.from_single_view(
                id=i,
                view=w.get_view(
                    (
                        # if the requested view is a CompositeFilter, and the widget has
                        # that CompositeFilter in its views, return that view. But if dashboard
                        # has a mix of grouped and ungrouped widgets, the ungrouped widgets will
                        # not have a view for the CompositeFilter, so in that case request `None`.
                        view if not list(w.views) == [None] else None
                    )
                ),
            )
            for i, w in enumerate(self.widgets)
        ]

    def _iter_views_json(
        self,
    ) -> Generator[tuple[str, list[EmumeratedWidgetSingleView]], None, None]:
        """Iterate over all possible views for the dashboard, yielding key:value pairs for each,
        in which the keys are a JSON-stringified representation of the views key, and the values
        are JSON-serializable dictionaries of the widget view.
        """
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
    def views_json(self) -> dict[str, list[EmumeratedWidgetSingleView]]:
        """A JSON-serializable dictionary for all possible views of the dashboard,
        keyed by JSON-stringified representations of the views keys.
        """
        return {k: v for k, v in self._iter_views_json()}

    @property
    def rjsf_filters_json(self) -> dict | None:
        """The JSON-serializable representation of the React JSON Schema Form filters."""
        return (
            ReactJSONSchemaFormFilters(
                options={
                    g.index_name: RJSFFilter(
                        property=RJSFFilterProperty(
                            type="string",
                            oneOf=[
                                oneOf(const=choice, title=choice.title())
                                for choice in choices
                            ],
                            default=choices[0],
                        ),
                        uiSchema=RJSFFilterUiSchema(
                            title=(
                                g.display_name or g.index_name.title().replace("_", " ")
                            ),
                            help=g.help_text or None,
                        ),
                    )
                    for g, choices in self.grouper_choices.items()
                }
            ).model_dump()
            if self.grouper_choices is not None
            else None
        )

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        """The method called by `.model_dump()` to serialize the model to a dictionary."""
        return DashboardJson(
            **{
                "filters": self.rjsf_filters_json,
                "views": self.views_json,
                "metadata": self.metadata,
                "layout": [],  # this is a placeholder for future use by server
            }
        ).model_dump()


def composite_filters_to_grouper_choices_dict(
    groupers: list[Grouper],
    keys: list[CompositeFilter | None],
) -> dict[Grouper, list[IndexValue]]:
    """Converts a set of Groupers and a list of composite filters
    to a dict of grouper choices.

    Examples:

    ```python
    >>> groupers = [Grouper(index_name="animal_name"), Grouper(index_name="month")]
    >>> keys = [
    ...     (('animal_name', '=', 'Ao'), ('month', '=', 'February')),
    ...     (('animal_name', '=', 'Ao'), ('month', '=', 'January')),
    ...     (('animal_name', '=', 'Bo'), ('month', '=', 'February')),
    ...     (('animal_name', '=', 'Bo'), ('month', '=', 'January')),
    ... ]
    >>> choices = composite_filters_to_grouper_choices_dict(groupers, keys)
    >>> {g.index_name: c for g, c in choices.items()}
    {'animal_name': ['Ao', 'Bo'], 'month': ['February', 'January']}

    ```
    """
    choices: dict[Grouper, list[IndexValue]] = {}

    def get_grouper(index_name: IndexName) -> Grouper:
        return next(g for g in groupers if g.index_name == index_name)

    for k in keys:
        if k is not None:
            for index_name, _, value in k:
                if get_grouper(index_name) not in choices:
                    choices[get_grouper(index_name)] = []
                if value not in choices[get_grouper(index_name)]:
                    choices[get_grouper(index_name)].append(value)

    for g in choices:
        # TODO: sort by logical order for the type of grouper (e.g. month names, not alphabetically)
        choices[g].sort()

    return choices


GroupedOrSingleWidget = GroupedWidget | WidgetSingleView

FlatWidgetList = (
    list[GroupedOrSingleWidget] | list[GroupedWidget] | list[WidgetSingleView]
)

AllNestedWidgetList = list[list[GroupedOrSingleWidget]]
PartiallyNestedWidgetList = list[list[GroupedOrSingleWidget] | GroupedOrSingleWidget]
NestedWidgetList = AllNestedWidgetList | PartiallyNestedWidgetList


def _flatten(possibly_nested: NestedWidgetList | FlatWidgetList) -> FlatWidgetList:
    """Transform a possibly nested list of widgets into a flat list of widgets.

    Only works for max depth 2.

    Examples:

    ```python
    >>> _flatten([[1, 2], 3, 4])
    [1, 2, 3, 4]
    >>> _flatten([1, [2, 3], 4])
    [1, 2, 3, 4]
    >>> _flatten([1, 2, 3, 4])
    [1, 2, 3, 4]

    ```

    """
    flat = []

    for item in possibly_nested:
        if isinstance(item, list):
            flat.extend(
                item
            )  # Directly extend with the sublist since we assume max depth 2
        else:
            flat.append(item)

    return flat


@task
def gather_dashboard(
    title: Annotated[str, Field(description="The title of the dashboard")],
    description: Annotated[str, Field(description="The description of the dashboard")],
    widgets: Annotated[
        NestedWidgetList | FlatWidgetList | GroupedOrSingleWidget,
        Field(description="The widgets to display.", exclude=True),
    ],
    groupers: Annotated[
        list[Grouper] | SkipJsonSchema[None],
        Field(
            description="""\
            A list of groupers that are used to group the widgets.
            If all widgets are ungrouped, this field defaults to `None`.
            """,
            exclude=True,
        ),
    ] = None,
) -> Annotated[Dashboard, Field()]:
    # if the input is any kind of list, try to flatten it because it might be nested
    # if not a list, make it a single-element list to allow uniform handling below
    as_flat_list = _flatten(widgets) if isinstance(widgets, list) else [widgets]
    # then regardless of element type(s), parse to uniform flat list of GroupedWidgets
    grouped_widgets = [
        GroupedWidget.from_single_view(w) if isinstance(w, WidgetSingleView) else w
        for w in as_flat_list
    ]
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
        grouper_choices = composite_filters_to_grouper_choices_dict(
            groupers, keys_sample
        )
    return Dashboard(
        widgets=grouped_widgets,
        grouper_choices=(grouper_choices if groupers else None),
        keys=(keys_sample if groupers else None),  # type: ignore[arg-type]
        metadata=Metadata(title=title, description=description),
    )
