import logging
from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


@task
def sort_values(
    df: AnyDataFrame,
    column_name: Annotated[
        str, Field(description="The column name to sort values by.")
    ],
    ascending: Annotated[bool, Field(description="Sort ascending if true")] = True,
    na_position: Annotated[
        Literal["first", "last"],
        Field(description="Where to place NaN values in the sort"),
    ] = "last",
) -> AnyDataFrame:
    return df.sort_values(by=column_name, ascending=ascending, na_position=na_position)
