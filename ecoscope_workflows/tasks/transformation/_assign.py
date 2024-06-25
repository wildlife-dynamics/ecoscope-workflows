from operator import attrgetter
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def assign_from_column_attribute(
    df: DataFrame[JsonSerializableDataFrameModel],
    column_name: Annotated[str, Field(description="New column name.")],
    dotted_attribute_name: Annotated[str, Field(description="Dotted attribute name.")],
) -> DataFrame[JsonSerializableDataFrameModel]:
    """
    Assigns a new column to the DataFrame based on the value of the dotted attribute name.

    Args:
        df (DataFrame[JsonSerializableDataFrameModel]): The input DataFrame to be transformed.
        column_name (str): New column name.
        dotted_attribute_name (str): Dotted attribute name.

    Returns:
        DataFrame[JsonSerializableDataFrameModel]: The transformed DataFrame.
    """
    return df.assign(**{column_name: lambda x: attrgetter(dotted_attribute_name)(x)})
