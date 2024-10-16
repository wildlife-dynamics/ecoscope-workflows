import logging
from typing import Annotated, Literal, Union

from ecoscope_workflows_core.annotations import AnyDataFrame
from ecoscope_workflows_core.decorators import task
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

logger = logging.getLogger(__name__)

ClassificationMethod = Literal[
    "equal_interval",
    "quantile",
    "fisher_jenks",
    "std_mean",
    "max_breaks",
    "natural_breaks",
]


class SharedArgs(BaseModel):
    scheme: ClassificationMethod = Field("equal_interval", exclude=True)
    k: int = 5


class QuantileArgs(SharedArgs):
    scheme: ClassificationMethod = Field("quantile", exclude=True)


class FisherJenksArgs(SharedArgs):
    scheme: ClassificationMethod = Field("fisher_jenks", exclude=True)


class StdMeanArgs(BaseModel):
    scheme: ClassificationMethod = Field("std_mean", exclude=True)
    multiples: list[int] = [-2, -1, 1, 2]
    anchor: bool = False


class MaxBreaksArgs(SharedArgs):
    scheme: ClassificationMethod = Field("max_breaks", exclude=True)
    mindiff: float = 0


class NaturalBreaksArgs(SharedArgs):
    scheme: ClassificationMethod = Field("natural_breaks", exclude=True)
    initial: int = 10


ClassificationArgs = Annotated[
    Union[
        SharedArgs,
        StdMeanArgs,
        MaxBreaksArgs,
        NaturalBreaksArgs,
        QuantileArgs,
        FisherJenksArgs,
    ],
    Field(discriminator="scheme"),
]


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
    classification_options: Annotated[
        ClassificationArgs,
        Field(description="Classification scheme and its arguments."),
    ] = SharedArgs(),
) -> AnyDataFrame:
    """
    Classifies a dataframe column using specified classification scheme.

    Args:
        dataframe (pd.DatFrame): The input data.
        input_column_name (str): The dataframe column to classify.
        output_column_name (str): The dataframe column that will contain the classification.
            Defaults to "<input_column_name>_classified"
        labels (list[str]): labels of bins, use bin edges if labels==None.

        classification_options:
            Classification scheme and its arguments.
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
    from ecoscope.analysis.classifier import apply_classification  # type: ignore[import-untyped]

    return apply_classification(
        df,
        input_column_name=input_column_name,
        output_column_name=output_column_name,
        labels=labels,
        scheme=classification_options.scheme,
        **classification_options.model_dump(exclude_none=True),  # type: ignore[union-attr]
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
    from ecoscope.analysis.classifier import apply_color_map  # type: ignore[import-untyped]

    return apply_color_map(
        dataframe=df,
        input_column_name=input_column_name,
        cmap=colormap,
        output_column_name=output_column_name,
    )
