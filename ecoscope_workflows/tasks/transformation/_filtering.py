import logging
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed

logger = logging.getLogger(__name__)


@distributed
def filter_dataframe(
    df: DataFrame[JsonSerializableDataFrameModel],
    expr: Annotated[str, Field(description="The boolean expr to filter a dataframe.")],
) -> DataFrame[JsonSerializableDataFrameModel]:
    """
    Filter a DataFrame based on a boolean expression. To be safe, we only allow numexpr as the query engine for now.

    Args:
        df (DataFrame[JsonSerializableDataFrameModel]): The DataFrame to be filtered.
        expr (str): The boolean expression to filter the DataFrame.

    Returns:
        DataFrame[JsonSerializableDataFrameModel]: The filtered DataFrame.

    """
    logger.info("Performing query on a dataframe. expr: %s", expr)
    df = df.query(expr, engine="numexpr")
    return df
