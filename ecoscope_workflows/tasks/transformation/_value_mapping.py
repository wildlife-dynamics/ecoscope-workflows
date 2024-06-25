from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def map_values(
    df: DataFrame[JsonSerializableDataFrameModel],
    column_name: Annotated[str, Field(description="The column name to map.")],
    value_map: Annotated[
        dict[str, str], Field(default={}, description="A dictionary of values to map.")
    ],
    preserve_values: Annotated[
        bool,
        Field(default=False, description="Whether to preserve values not in the map."),
    ],
) -> DataFrame[JsonSerializableDataFrameModel]:
    if preserve_values:
        df[column_name] = df[column_name].map(value_map).fillna(df[column_name])
    else:
        df[column_name] = df[column_name].map(value_map)
    return df
