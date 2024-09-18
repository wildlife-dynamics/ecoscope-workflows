import logging
from typing import Annotated, Literal, cast

from pydantic import Field

from ecoscope_workflows.core.annotations import AnyDataFrame
from ecoscope_workflows.core.decorators import task

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
    return cast(
        AnyDataFrame,
        df.sort_values(by=column_name, ascending=ascending, na_position=na_position),
    )
