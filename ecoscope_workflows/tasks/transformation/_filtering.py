from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def filter_dataframe(
    df: DataFrame[JsonSerializableDataFrameModel],
    expr: Annotated[str, Field(description="The boolean expr to filter a dataframe.")],
) -> DataFrame[JsonSerializableDataFrameModel]:
    df = df.query(expr)
    return df
