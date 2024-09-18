import logging
from typing import Annotated, cast

from pydantic import Field

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


@task
def map_values(
    df: AnyDataFrame,
    column_name: Annotated[str, Field(description="The column name to map.")],
    value_map: Annotated[
        dict[str, str], Field(default={}, description="A dictionary of values to map.")
    ],
    preserve_values: Annotated[
        bool,
        Field(default=False, description="Whether to preserve values not in the map."),
    ],
) -> AnyDataFrame:
    if preserve_values:
        df[column_name] = df[column_name].map(value_map).fillna(df[column_name])
    else:
        df[column_name] = df[column_name].map(value_map)
    return cast(AnyDataFrame, df)


@task
def map_columns(
    df: AnyDataFrame,
    drop_columns: Annotated[
        list[str], Field(default=[], description="List of columns to drop.")
    ],
    retain_columns: Annotated[
        list[str],
        Field(
            default=[],
            description="""List of columns to retain with the order specified by the list.
                        "Keep all the columns if the list is empty.""",
        ),
    ],
    rename_columns: Annotated[
        dict[str, str],
        Field(default={}, description="Dictionary of columns to rename."),
    ],
) -> AnyDataFrame:
    """
    Maps and transforms the columns of a DataFrame based on the provided parameters. The order of the operations is as
    follows: drop columns, retain/reorder columns, and rename columns.

    Args:
        df (DataFrame[JsonSerializableDataFrameModel]): The input DataFrame to be transformed.
        drop_columns (list[str]): List of columns to drop from the DataFrame.
        retain_columns (list[str]): List of columns to retain. The order of columns will be preserved.
        rename_columns (dict[str, str]): Dictionary of columns to rename.

    Returns:
        DataFrame[JsonSerializableDataFrameModel]: The transformed DataFrame.

    Raises:
        KeyError: If any of the columns specified are not found in the DataFrame.
    """
    if "geometry" in drop_columns:
        logger.warning(
            "'geometry' found in drop_columns, which may affect spatial operations."
        )

    if "geometry" in rename_columns.keys():
        logger.warning(
            "'geometry' found in rename_columns, which may affect spatial operations."
        )

    df = df.drop(columns=drop_columns)
    if retain_columns:
        if any(col not in df.columns for col in retain_columns):
            raise KeyError(f"Columns {retain_columns} not all found in DataFrame.")
        df = df.reindex(columns=retain_columns)  # type: ignore[assignment]
    if rename_columns:
        if any(col not in df.columns for col in rename_columns):
            raise KeyError(f"Columns {rename_columns} not all found in DataFrame.")
        df = df.rename(columns=rename_columns)  # type: ignore[assignment]

    return cast(AnyDataFrame, df)
