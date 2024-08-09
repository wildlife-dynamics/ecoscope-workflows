from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task


@task
def aggregate(
    df: AnyDataFrame,
    column_name: Annotated[str, Field(description="Column to aggregate")],
    func_name: Annotated[
        Literal["count", "mean", "sum", "nunique"],
        Field(description="The method of aggregation"),
    ],
) -> Annotated[int | float, Field(description="The result of the aggregation")]:
    match func_name.upper():
        case "COUNT":
            return len(df)
        case "MEAN":
            return df[column_name].mean()
        case "SUM":
            return df[column_name].sum()
        case "NUNIQUE":
            return df[column_name].nunique()
        case _:
            raise ValueError(f"Unknown aggregation function: {func_name}")
