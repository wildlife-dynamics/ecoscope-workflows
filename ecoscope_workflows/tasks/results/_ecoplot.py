from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import task


@task
def draw_ecoplot(
    dataframe: DataFrame[JsonSerializableDataFrameModel],
    group_by: Annotated[str, Field(description="The dataframe column to group by.")],
    x_axis: Annotated[
        str, Field(description="The dataframe column to plot in the x axis.")
    ],
    y_axis: Annotated[
        str, Field(description="The dataframe column to plot in the y axis.")
    ],
    style_kws: Annotated[
        dict,
        Field(description="Style arguments passed to plotly.graph_objects.Scatter."),
    ],
) -> Annotated[str, Field()]:
    """
    Generates an EcoPlot from the provided params

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    group_by (str): The dataframe column to group by.
    x_axis (str): The dataframe column to plot in the x axis.
    y_axis (str): The dataframe column to plot in the y axis.
    style_kws (str): Style arguments passed to plotly.graph_objects.Scatter.

    Returns:
    The generated plot html as a string
    """
    import ecoscope.plotting as plotting

    grouped = dataframe.groupby(group_by)

    data = plotting.EcoPlotData(
        grouped=grouped,
        x_col=x_axis,
        y_col=y_axis,
        **style_kws,
    )

    plot = plotting.ecoplot(
        data=[data],
    )

    return plot.to_html(
        default_height="100%",
        default_width="100%",
        config={
            "autosizable": True,
            "fillFrame": True,
            "responsive": True,
            "displayModeBar": False,
        },
    )
