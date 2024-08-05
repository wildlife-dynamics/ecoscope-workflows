import logging
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


@task
def explode(
    df: DataFrame[JsonSerializableDataFrameModel],
    column_name: Annotated[str, Field(description="The column name to explode.")],
    ignore_index: Annotated[bool, Field(description="Whether to ignore the index.")],
) -> DataFrame[JsonSerializableDataFrameModel]:
    return df.explode(column_name, ignore_index)
