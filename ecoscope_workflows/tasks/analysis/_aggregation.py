from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task


ColumnName = Annotated[str, Field(description="Column to aggregate")]


@task
def dataframe_count(
    df: AnyDataFrame,
) -> Annotated[int, Field(description="The number of rows in the DataFrame")]:
    return len(df)


@task
def dataframe_column_mean(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[float, Field(description="The mean of the column")]:
    return df[column_name].mean()


@task
def dataframe_column_sum(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[float, Field(description="The sum of the column")]:
    return df[column_name].sum()


@task
def dataframe_column_nunique(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[int, Field(description="The number of unique values in the column")]:
    return df[column_name].nunique()
