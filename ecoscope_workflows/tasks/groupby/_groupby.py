from typing import Annotated

from pydantic import BaseModel, Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.indexes import CompositeFilter, IndexName, IndexValue
from ecoscope_workflows.decorators import task


def _groupkey_to_composite_filter(
    groupers: list[IndexName], index_values: tuple[IndexValue, ...]
) -> CompositeFilter:
    """Given the list of `groupers` used to group a dataframe, convert a group key
    tuple (the pandas native representation) to a composite filter (our representation).
    """
    return tuple((index, "=", value) for index, value in zip(groupers, index_values))


class Grouper(BaseModel):
    index_name: IndexName
    display_name: str | None = None
    help_text: str | None = None


@task
def set_groupers(
    groupers: Annotated[
        list[str], Field(description="Index(es) and/or column(s) to group by")
    ],
    # TODO: support setting display names and help text
) -> Annotated[
    list[Grouper],
    Field(description="Groupers with optional display names and help text"),
]:
    return [Grouper(index_name=grouper) for grouper in groupers]


@task
def split_groups(
    df: AnyDataFrame,
    groupers: Annotated[
        list[Grouper], Field(description="Index(es) and/or column(s) to group by")
    ],
) -> Annotated[
    list[tuple[CompositeFilter, AnyDataFrame]],
    Field(
        description="""\
        List of 2-tuples of key:value pairs. Each key:value pair consists of a composite
        filter (the key) and the corresponding subset of the input dataframe (the value).
        """
    ),
]:
    # TODO: configurable cardinality constraint with a default?
    grouper_index_names = [g.index_name for g in groupers]
    grouped = df.groupby(grouper_index_names)
    return [
        (_groupkey_to_composite_filter(grouper_index_names, index_value), group)
        for index_value, group in grouped
    ]