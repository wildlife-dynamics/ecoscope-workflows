from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def map_columns(
    df: DataFrame[JsonSerializableDataFrameModel],
    drop_columns: Annotated[list[str], Field()],
    retain_columns: Annotated[list[str], Field()],
    rename_columns: Annotated[dict[str, str], Field()],
) -> DataFrame[JsonSerializableDataFrameModel]:

    df.drop(columns=drop_columns, inplace=True)
    if retain_columns:
        df.reindex(columns=[retain_columns], inplace=True)
    if rename_columns:
        df.rename(columns=rename_columns, inplace=True)

    return df
