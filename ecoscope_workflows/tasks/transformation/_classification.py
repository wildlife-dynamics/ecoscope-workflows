import logging
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows.annotations import AnyDataFrame
from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


class SharedArgs(BaseModel):
    k: int = 5


class StdMeanArgs(BaseModel):
    multiples: list[int] = [-2, -1, 1, 2]
    anchor: bool = False


class MaxBreaksArgs(SharedArgs):
    mindiff: float = 0


class NaturalBreaksArgs(SharedArgs):
    initial: int = 10


@task
def apply_classification(
    df: Annotated[
        AnyDataFrame,
        Field(description="The dataframe to classify.", exclude=True),
    ],
    input_column_name: Annotated[
        str, Field(description="The dataframe column to classify.")
    ],
    output_column_name: Annotated[
        str | SkipJsonSchema[None],
        Field(
            description="The dataframe column that will contain the classification values."
        ),
    ] = None,
    labels: Annotated[
        list[str] | SkipJsonSchema[None],
        Field(
            description="Labels of classification bins, uses bin edges if not provied."
        ),
    ] = None,
    scheme: Annotated[
        Literal[
            "equal_interval",
            "natural_breaks",
            "quantile",
            "std_mean",
            "max_breaks",
            "fisher_jenks",
        ],
        Field(description="The classification scheme to use."),
    ] = "equal_interval",
    classification_options: Annotated[
        NaturalBreaksArgs
        | MaxBreaksArgs
        | StdMeanArgs
        | SharedArgs
        | SkipJsonSchema[None],
        Field(description="Additional options specific to the classification scheme."),
    ] = None,
) -> AnyDataFrame:
    """
    Classifies a dataframe column using specified classification scheme.

    Args:
        dataframe (pd.DatFrame): The input data.
        input_column_name (str): The dataframe column to classify.
        output_column_name (str): The dataframe column that will contain the classification.
            Defaults to "<input_column_name>_classified"
        labels (list[str]): labels of bins, use bin edges if labels==None.
        scheme (str): Classification scheme to use [equal_interval, natural_breaks, quantile, std_mean, max_breaks,
        fisher_jenks]

        classification_options:
            Additional keyword arguments specific to the classification scheme, passed to mapclassify.
            See below:

            Applicable to equal_interval, natural_breaks, quantile, max_breaks & fisher_jenks:
                k (int): The number of classes required

            Applicable only to natural_breaks:
                initial (int): The number of initial solutions generated with different centroids.
                    The best of initial results are returned.

            Applicable only to max_breaks:
                mindiff (float): The minimum difference between class breaks.

            Applicable only to std_mean:
                multiples (numpy.array): The multiples of the standard deviation to add/subtract
                    from the sample mean to define the bins.
                anchor (bool): Anchor upper bound of one class to the sample mean.

            For more information, see https://pysal.org/mapclassify/api.html

    Returns:
        The input dataframe with a classification column appended.
    """
    from ecoscope.analysis.classifier import apply_classification

    return apply_classification(
        df,
        input_column_name=input_column_name,
        output_column_name=output_column_name,
        labels=labels,
        scheme=scheme,
        **classification_options.model_dump(exclude_none=True),
    )


@task
def apply_color_map(
    df: Annotated[
        AnyDataFrame,
        Field(description="The dataframe to apply the color map to.", exclude=True),
    ],
    input_column_name: Annotated[
        str, Field(description="The name of the column with categorical values.")
    ],
    colormap: Annotated[
        str | list[str],
        Field(
            description="Either a named mpl.colormap or a list of string hex values."
        ),
    ] = "viridis",
    output_column_name: Annotated[
        str | SkipJsonSchema[None],
        Field(description="The dataframe column that will contain the color values."),
    ] = None,
) -> AnyDataFrame:
    """
    Adds a color column to the dataframe based on the categorical values in the specified column.

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    column_name (str): The name of the column with categorical values.
    colormap (str): Either a named mpl.colormap or a list of string hex values.
    output_column_name (str): The dataframe column that will contain the classification.
            Defaults to "<input_column_name>_colormap"

    Returns:
    pd.DataFrame: The dataframe with an additional color column.
    """
    from ecoscope.analysis.classifier import apply_color_map

    return apply_color_map(
        dataframe=df,
        input_column_name=input_column_name,
        cmap=colormap,
        output_column_name=output_column_name,
    )
