from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def assign_temporal_column(
    df: DataFrame[JsonSerializableDataFrameModel],
    col_name: Annotated[str, Field()],
    time_col: Annotated[str, Field()],
    directive: Annotated[str, Field()],
) -> DataFrame[JsonSerializableDataFrameModel]:
    return df.assign(**{col_name: df[time_col].dt.strftime(directive)})
