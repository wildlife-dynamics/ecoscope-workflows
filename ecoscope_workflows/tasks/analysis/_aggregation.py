from operator import add, floordiv, mod, mul, pow, sub, truediv
from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame, AnyGeoDataFrame
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
    return round(df[column_name].mean(), 2)


@task
def dataframe_column_sum(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[float, Field(description="The sum of the column")]:
    return round(df[column_name].sum(), 2)


@task
def dataframe_column_max(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[float, Field(description="The max of the column")]:
    return round(df[column_name].max(), 2)


@task
def dataframe_column_min(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[float, Field(description="The min of the column")]:
    return round(df[column_name].min(), 2)


@task
def dataframe_column_nunique(
    df: AnyDataFrame,
    column_name: ColumnName,
) -> Annotated[int, Field(description="The number of unique values in the column")]:
    return df[column_name].nunique()


operations = {
    "add": add,
    "subtract": sub,
    "multiply": mul,
    "divide": truediv,
    "floor_divide": floordiv,
    "modulo": mod,
    "power": pow,
}

Operations = Literal[
    "add", "subtract", "multiply", "divide", "floor_divide", "modulo", "power"
]


@task
def apply_arithmetic_operation(
    a: Annotated[float | int, Field(description="The first number")],
    b: Annotated[float | int, Field(description="The second number")],
    operation: Annotated[
        Operations, Field(description="The arithmetic operation to apply")
    ],
) -> Annotated[
    float | int, Field(description="The result of the arithmetic operation")
]:
    return round(operations[operation](a, b), 2)


@task
def get_day_night_ratio(
    df: AnyGeoDataFrame,
) -> Annotated[float, Field(description="Daynight ratio")]:
    from ecoscope.analysis import astronomy

    return round(astronomy.get_daynight_ratio(df), 2)
