from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import task


class LineStyle(BaseModel):
    color: str | SkipJsonSchema[None] = None


class PlotStyle(BaseModel):
    xperiodalignment: str | SkipJsonSchema[None] = None
    marker_colors: list[str] | SkipJsonSchema[None] = None
    textinfo: str | SkipJsonSchema[None] = None
    line: LineStyle | SkipJsonSchema[None] = None


class PlotCategoryStyle(BaseModel):
    marker_color: str | SkipJsonSchema[None] = None


class GroupedPlotStyle(BaseModel):
    category: str
    plot_style: PlotCategoryStyle


class LayoutStyle(BaseModel):
    font_color: str | SkipJsonSchema[None] = None
    font_style: str | SkipJsonSchema[None] = None
    plot_bgcolor: str | SkipJsonSchema[None] = None
    showlegend: bool | SkipJsonSchema[None] = None


class BarLayoutStyle(LayoutStyle):
    bargap: Annotated[float, Field(ge=0.0, le=1.0)] | SkipJsonSchema[None] = None
    bargroupgap: Annotated[float, Field(ge=0.0, le=1.0)] | SkipJsonSchema[None] = None


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
    plot_style: Annotated[
        PlotStyle | SkipJsonSchema[None],
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
    plot_style (PlotStyle): Style arguments passed to plotly.graph_objects.Scatter.

    Returns:
    The generated plot html as a string
    """
    import ecoscope.plotting as plotting

    grouped = dataframe.groupby(group_by)

    data = plotting.EcoPlotData(
        grouped=grouped,
        x_col=x_axis,
        y_col=y_axis,
        **(plot_style.model_dump(exclude_none=True) if plot_style else {}),
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


@task
def draw_time_series_bar_chart(
    dataframe: DataFrame[JsonSerializableDataFrameModel],
    x_axis: Annotated[
        str, Field(description="The dataframe column to plot in the x/time axis.")
    ],
    y_axis: Annotated[
        str, Field(description="The dataframe column to plot in the y axis.")
    ],
    category: Annotated[
        str, Field(description="The dataframe column to stack in the y axis.")
    ],
    agg_function: Annotated[
        Literal["count", "mean", "sum", "min", "max"],
        Field(description="The aggregate function to apply to the group."),
    ],
    time_interval: Annotated[
        Literal["year", "month", "week", "day", "hour"],
        Field(description="Sets the time interval of the x axis."),
    ],
    grouped_styles: Annotated[
        list[GroupedPlotStyle],
        Field(
            description="Style arguments passed to plotly.graph_objects.Bar and applied to individual groups."
        ),
    ] = [],
    plot_style: Annotated[
        PlotStyle | SkipJsonSchema[None],
        Field(description="Additional style kwargs passed to go.Pie()."),
    ] = None,
    layout_style: Annotated[
        BarLayoutStyle | SkipJsonSchema[None],
        Field(description="Additional kwargs passed to plotly.go.Figure(layout)."),
    ] = None,
) -> Annotated[str, Field()]:
    """
    Generates a stacked time series bar chart from the provided params

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    x_axis (str): The dataframe column to plot in the x axis.
    y_axis (str): The dataframe column to plot in the y axis.
    stack_column (str): The dataframe column to stack in the y axis.
    agg_function (str): The aggregate function to apply to the group.
    agg_function (str): Sets the time interval of the x axis.
    grouped_styles (list[GroupedPlotStyle]): Style arguments passed to plotly.graph_objects.Bar and applied to individual groups.
    plot_style (PlotStyle): Style arguments passed to plotly.graph_objects.Bar and applied to all groups.
    layout_style (LayoutStyle): Additional kwargs passed to plotly.go.Figure(layout).

    Returns:
    The generated chart html as a string
    """
    import datetime

    from ecoscope.plotting import EcoPlotData, stacked_bar_chart

    layout_kws = layout_style.model_dump(exclude_none=True) if layout_style else {}

    match time_interval:
        case "year":
            dataframe["truncated_time"] = dataframe[x_axis].apply(
                lambda x: datetime.datetime(x.year, 1, 1)
            )
            layout_kws["xaxis_dtick"] = "M12"
        case "month":
            dataframe["truncated_time"] = dataframe[x_axis].apply(
                lambda x: datetime.datetime(x.year, x.month, 1)
            )
            layout_kws["xaxis_dtick"] = "M1"
        case "week":
            dataframe["truncated_time"] = dataframe[x_axis].apply(
                lambda x: datetime.datetime(x.year, x.month, x.day)
            )
            layout_kws["xaxis_dtick"] = 604800000
        case "day":
            dataframe["truncated_time"] = dataframe[x_axis].apply(
                lambda x: datetime.datetime(x.year, x.month, x.day)
            )
            layout_kws["xaxis_dtick"] = 86400000
        case "hour":
            dataframe["truncated_time"] = dataframe[x_axis].apply(
                lambda x: datetime.datetime(x.year, x.month, x.day, x.hour)
            )
            layout_kws["xaxis_dtick"] = 3600000

    grouped = dataframe.groupby(["truncated_time", category])

    groupby_style = {
        group.category: group.plot_style.model_dump(exclude_none=True)
        for group in grouped_styles
    }

    data = EcoPlotData(
        grouped=grouped,
        x_col="truncated_time",
        y_col=y_axis,
        groupby_style=groupby_style,
        **(plot_style.model_dump(exclude_none=True) if plot_style else {}),
    )

    plot = stacked_bar_chart(
        data=data,
        agg_function=agg_function,
        stack_column=category,
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


@task
def draw_pie_chart(
    dataframe: DataFrame[JsonSerializableDataFrameModel],
    value_column: Annotated[
        str,
        Field(
            description="The name of the dataframe column to pull slice values from."
        ),
    ],
    label_column: Annotated[
        str | SkipJsonSchema[None],
        Field(
            description="The name of the dataframe column to label slices with, required if the data in value_column is numeric."
        ),
    ] = None,
    plot_style: Annotated[
        PlotStyle | SkipJsonSchema[None],
        Field(description="Additional style kwargs passed to go.Pie()."),
    ] = None,
    layout_style: Annotated[
        LayoutStyle | SkipJsonSchema[None],
        Field(description="Additional kwargs passed to plotly.go.Figure(layout)."),
    ] = None,
) -> Annotated[str, Field()]:
    """
    Generates a pie chart from the provided params

    Args:
    dataframe (pd.DataFrame): The input dataframe.
    value_column (str): The name of the dataframe column to pull slice values from.
    label_column (str): The name of the dataframe column to label slices with, required if the data in value_column is numeric.
    plot_style (PlotStyle): Additional style kwargs passed to go.Pie().
    layout_style (LayoutStyle): Additional kwargs passed to plotly.go.Figure(layout).

    Returns:
    The generated chart html as a string
    """
    from ecoscope.plotting import pie_chart

    plot = pie_chart(
        data=dataframe,
        value_column=value_column,
        label_column=label_column,
        style_kwargs=plot_style.model_dump(exclude_none=True) if plot_style else {},
        layout_kwargs=layout_style.model_dump(exclude_none=True)
        if layout_style
        else {},
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
