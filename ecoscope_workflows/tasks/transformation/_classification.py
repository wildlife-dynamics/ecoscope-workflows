from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def classify_categorical_value(
    df: DataFrame[JsonSerializableDataFrameModel],
    column_name: Annotated[
        str, Field(description="The name of the column with categorical values.")
    ],
    colormap_name: Annotated[
        str, Field(default="viridis", description="matplotlib.colors.Colormap")
    ],
) -> DataFrame[JsonSerializableDataFrameModel]:
    """
    Adds a color column to the dataframe based on the categorical values in the specified column.

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    column_name (str): The name of the column with categorical values.
    colormap_name (str): The name of the matplotlib colormap to use.

    Returns:
    pd.DataFrame: The dataframe with an additional color column.
    """

    import matplotlib

    # Get the colormap
    colormap = matplotlib.colormaps[colormap_name]

    # Get unique categories
    unique_categories = df[column_name].unique()

    # Create a dictionary to map categories to colors
    colors = colormap(range(len(unique_categories)))
    category_colors = {
        category: colors[i] for i, category in enumerate(unique_categories)
    }

    # Add the color column to the dataframe
    df["label"] = df[column_name].map(category_colors)

    return df
