from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.indexes import CompositeFilter, IndexName, IndexValue
from ecoscope_workflows.decorators import distributed


def _groupkey_to_composite_filter(
    groupers: list[IndexName], index_values: tuple[IndexValue, ...]
) -> CompositeFilter:
    """Given the list of `groupers` used to group a dataframe, convert a group key
    tuple (the pandas native representation) to a composite filter (our representation).
    """
    return tuple((index, "=", value) for index, value in zip(groupers, index_values))


@distributed
def split_groups(
    df: AnyDataFrame,
    groupers: Annotated[
        str | list[str], Field(description="Index(es) and/or column(s) to group by")
    ],
) -> Annotated[
    dict[CompositeFilter, AnyDataFrame],
    Field(description="Dictionary of indexed groups"),
]:
    _groupers = groupers if isinstance(groupers, list) else [groupers]
    # TODO: configurable cardinality constraint with a default?
    grouped = df.groupby(_groupers)
    return {
        _groupkey_to_composite_filter(_groupers, index_value): group
        for index_value, group in grouped
    }
