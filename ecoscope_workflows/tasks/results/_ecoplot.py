from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
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


@distributed
def draw_stacked_bar_chart(
    dataframe: DataFrame[JsonSerializableDataFrameModel],
    x_axis: Annotated[
        str, Field(description="The dataframe column to plot in the x axis.")
    ],
    y_axis: Annotated[
        str, Field(description="The dataframe column to plot in the y axis.")
    ],
    stack_column: Annotated[
        str, Field(description="The dataframe column to stack in the y axis.")
    ],
    agg_function: Annotated[
        Literal["count", "mean", "sum", "min", "max"],
        Field(description="The aggregate function to apply to the group."),
    ],
    groupby_style_kws: Annotated[
        dict | None,
        Field(
            description="Style arguments passed to plotly.graph_objects.Bar and applied to individual groups."
        ),
    ],
    style_kws: Annotated[
        dict | None,
        Field(
            description="Style arguments passed to plotly.graph_objects.Bar and applied to all groups."
        ),
    ],
    layout_kws: Annotated[
        dict | None,
        Field(description="Style arguments passed to plotly.graph_objects.Figure."),
    ],
) -> Annotated[str, Field()]:
    """
    Generates a stacked bar chart from the provided params

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    x_axis (str): The dataframe column to plot in the x axis.
    y_axis (str): The dataframe column to plot in the y axis.
    stack_column (str): The dataframe column to stack in the y axis.
    agg_function (str): The aggregate function to apply to the group.
    groupby_style_kws (dict): Style arguments passed to plotly.graph_objects.Bar and applied to individual groups.
    style_kws (dict): Style arguments passed to plotly.graph_objects.Bar and applied to all groups.
    layout_kws (dict): Style arguments passed to plotly.graph_objects.Figure.

    Returns:
    The generated plot html as a string
    """
    from ecoscope.plotting import stacked_bar_chart, EcoPlotData

    grouped = dataframe.groupby([x_axis, stack_column])

    data = EcoPlotData(
        grouped=grouped,
        x_col=x_axis,
        y_col=y_axis,
        groupby_style=groupby_style_kws,
        **style_kws,
    )

    plot = stacked_bar_chart(
        data=data,
        agg_function=agg_function,
        stack_column=stack_column,
        layout_kwargs=layout_kws,
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
