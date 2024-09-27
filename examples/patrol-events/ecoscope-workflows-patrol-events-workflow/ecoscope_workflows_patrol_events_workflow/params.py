# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "bff9fb1063b3c799764280e1c82c2f8d8142f807c786674db06e2a56a9bfdc5a"


from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, confloat


class Pe(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    since: str = Field(..., description="Start date", title="Since")
    until: str = Field(..., description="End date", title="Until")
    patrol_type: List[str] = Field(
        ..., description="list of UUID of patrol types", title="Patrol Type"
    )
    status: List[str] = Field(
        ...,
        description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'",
        title="Status",
    )


class Directive(str, Enum):
    field_a = "%a"
    field_A = "%A"
    field_b = "%b"
    field_B = "%B"
    field_c = "%c"
    field_d = "%d"
    field_f = "%f"
    field_H = "%H"
    field_I = "%I"
    field_j = "%j"
    field_m = "%m"
    field_M = "%M"
    field_p = "%p"
    field_S = "%S"
    field_U = "%U"
    field_w = "%w"
    field_W = "%W"
    field_x = "%x"
    field_X = "%X"
    field_y = "%y"
    field_Y = "%Y"
    field_z = "%z"
    field__ = "%%"


class PeAddTemporalIndex(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    index_name: str = Field(
        ...,
        description="A name for the new index which will be added.",
        title="Index Name",
    )
    time_col: str = Field(
        ...,
        description="Name of existing column containing time data.",
        title="Time Col",
    )
    directive: Directive = Field(
        ..., description="A directive for formatting the time data.", title="Directive"
    )
    cast_to_datetime: Optional[bool] = Field(
        True,
        description="Whether to attempt casting `time_col` to datetime.",
        title="Cast To Datetime",
    )
    format: Optional[str] = Field(
        "mixed",
        description='            If `cast_to_datetime=True`, the format to pass to `pd.to_datetime`\n            when attempting to cast `time_col` to datetime. Defaults to "mixed".\n            ',
        title="Format",
    )


class PeColormap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    input_column_name: str = Field(
        ...,
        description="The name of the column with categorical values.",
        title="Input Column Name",
    )
    colormap: Optional[Union[str, List[str]]] = Field(
        "viridis",
        description="Either a named mpl.colormap or a list of string hex values.",
        title="Colormap",
    )
    output_column_name: Optional[str] = Field(
        None,
        description="The dataframe column that will contain the color values.",
        title="Output Column Name",
    )


class PeEcomapHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class PeMapWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class AggFunction(str, Enum):
    count = "count"
    mean = "mean"
    sum = "sum"
    min = "min"
    max = "max"


class TimeInterval(str, Enum):
    year = "year"
    month = "month"
    week = "week"
    day = "day"
    hour = "hour"


class PeBarChartHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class PeBarChartWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class PeMeshgrid(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    cell_width: Optional[int] = Field(
        5000, description="The width of a grid cell in meters.", title="Cell Width"
    )
    cell_height: Optional[int] = Field(
        5000, description="The height of a grid cell in meters.", title="Cell Height"
    )
    intersecting_only: Optional[bool] = Field(
        False,
        description="Whether to return only grid cells intersecting with the aoi.",
        title="Intersecting Only",
    )


class GeometryType(str, Enum):
    point = "point"
    line = "line"


class PeFeatureDensity(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    geometry_type: GeometryType = Field(
        ...,
        description="The geometry type of the provided geodataframe",
        title="Geometry Type",
    )


class FdColormap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    input_column_name: str = Field(
        ...,
        description="The name of the column with categorical values.",
        title="Input Column Name",
    )
    colormap: Optional[Union[str, List[str]]] = Field(
        "viridis",
        description="Either a named mpl.colormap or a list of string hex values.",
        title="Colormap",
    )
    output_column_name: Optional[str] = Field(
        None,
        description="The dataframe column that will contain the color values.",
        title="Output Column Name",
    )


class FdEcomapHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class FdMapWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class GroupedPeEcomapHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class GroupedPeMapWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class GroupedPePieChartHtmlUrls(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class GroupedPePieChartWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class GroupedPeFeatureDensity(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    geometry_type: GeometryType = Field(
        ...,
        description="The geometry type of the provided geodataframe",
        title="Geometry Type",
    )


class GroupedFdColormap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    input_column_name: str = Field(
        ...,
        description="The name of the column with categorical values.",
        title="Input Column Name",
    )
    colormap: Optional[Union[str, List[str]]] = Field(
        "viridis",
        description="Either a named mpl.colormap or a list of string hex values.",
        title="Colormap",
    )
    output_column_name: Optional[str] = Field(
        None,
        description="The dataframe column that will contain the color values.",
        title="Output Column Name",
    )


class GroupedFdEcomapHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class GroupedFdMapWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class PatrolDashboard(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the dashboard", title="Title")
    description: str = Field(
        ..., description="The description of the dashboard", title="Description"
    )


class Grouper(BaseModel):
    index_name: str = Field(..., title="Index Name")
    display_name: Optional[str] = Field(None, title="Display Name")
    help_text: Optional[str] = Field(None, title="Help Text")


class Coordinate(BaseModel):
    x: float = Field(..., title="X")
    y: float = Field(..., title="Y")


class LegendDefinition(BaseModel):
    label_column: str = Field(..., title="Label Column")
    color_column: str = Field(..., title="Color Column")


class LineWidthUnits(str, Enum):
    meters = "meters"
    pixels = "pixels"


class LayerType(str, Enum):
    point = "point"


class RadiusUnits(str, Enum):
    meters = "meters"
    pixels = "pixels"


class PointLayerStyle(BaseModel):
    auto_highlight: Optional[bool] = Field(False, title="Auto Highlight")
    opacity: Optional[float] = Field(1, title="Opacity")
    pickable: Optional[bool] = Field(True, title="Pickable")
    filled: Optional[bool] = Field(True, title="Filled")
    get_fill_color: Optional[Union[str, List[int], List[List[int]]]] = Field(
        None, title="Get Fill Color"
    )
    get_line_color: Optional[Union[str, List[int], List[List[int]]]] = Field(
        None, title="Get Line Color"
    )
    get_line_width: Optional[float] = Field(1, title="Get Line Width")
    fill_color_column: Optional[str] = Field(None, title="Fill Color Column")
    line_width_units: Optional[LineWidthUnits] = Field(
        "pixels", title="Line Width Units"
    )
    layer_type: Literal["point"] = Field("point", title="Layer Type")
    get_radius: Optional[float] = Field(1, title="Get Radius")
    radius_units: Optional[RadiusUnits] = Field("pixels", title="Radius Units")


class LayerType1(str, Enum):
    polygon = "polygon"


class PolygonLayerStyle(BaseModel):
    auto_highlight: Optional[bool] = Field(False, title="Auto Highlight")
    opacity: Optional[float] = Field(1, title="Opacity")
    pickable: Optional[bool] = Field(True, title="Pickable")
    filled: Optional[bool] = Field(True, title="Filled")
    get_fill_color: Optional[Union[str, List[int], List[List[int]]]] = Field(
        None, title="Get Fill Color"
    )
    get_line_color: Optional[Union[str, List[int], List[List[int]]]] = Field(
        None, title="Get Line Color"
    )
    get_line_width: Optional[float] = Field(1, title="Get Line Width")
    fill_color_column: Optional[str] = Field(None, title="Fill Color Column")
    line_width_units: Optional[LineWidthUnits] = Field(
        "pixels", title="Line Width Units"
    )
    layer_type: Literal["polygon"] = Field("polygon", title="Layer Type")
    extruded: Optional[bool] = Field(False, title="Extruded")
    get_elevation: Optional[float] = Field(1000, title="Get Elevation")


class LayerType2(str, Enum):
    polyline = "polyline"


class WidthUnits(str, Enum):
    meters = "meters"
    pixels = "pixels"


class PolylineLayerStyle(BaseModel):
    auto_highlight: Optional[bool] = Field(False, title="Auto Highlight")
    opacity: Optional[float] = Field(1, title="Opacity")
    pickable: Optional[bool] = Field(True, title="Pickable")
    layer_type: Literal["polyline"] = Field("polyline", title="Layer Type")
    get_color: Optional[Union[str, List[int], List[List[int]]]] = Field(
        None, title="Get Color"
    )
    get_width: Optional[float] = Field(1, title="Get Width")
    color_column: Optional[str] = Field(None, title="Color Column")
    width_units: Optional[WidthUnits] = Field("pixels", title="Width Units")
    cap_rounded: Optional[bool] = Field(True, title="Cap Rounded")


class LayerDefinition(BaseModel):
    geodataframe: Any = Field(..., title="Geodataframe")
    layer_style: Union[PolylineLayerStyle, PointLayerStyle, PolygonLayerStyle] = Field(
        ..., discriminator="layer_type", title="Layer Style"
    )
    legend: LegendDefinition


class Placement(str, Enum):
    top_left = "top-left"
    top_right = "top-right"
    bottom_left = "bottom-left"
    bottom_right = "bottom-right"
    fill = "fill"


class LegendStyle(BaseModel):
    placement: Optional[Placement] = Field("bottom-right", title="Placement")


class NorthArrowStyle(BaseModel):
    placement: Optional[Placement] = Field("top-left", title="Placement")
    style: Optional[Dict[str, Any]] = Field({"transform": "scale(0.8)"}, title="Style")


class BarLayoutStyle(BaseModel):
    font_color: Optional[str] = Field(None, title="Font Color")
    font_style: Optional[str] = Field(None, title="Font Style")
    plot_bgcolor: Optional[str] = Field(None, title="Plot Bgcolor")
    showlegend: Optional[bool] = Field(None, title="Showlegend")
    bargap: Optional[confloat(ge=0.0, le=1.0)] = Field(None, title="Bargap")
    bargroupgap: Optional[confloat(ge=0.0, le=1.0)] = Field(None, title="Bargroupgap")


class LineStyle(BaseModel):
    color: Optional[str] = Field(None, title="Color")


class PlotCategoryStyle(BaseModel):
    marker_color: Optional[str] = Field(None, title="Marker Color")


class PlotStyle(BaseModel):
    xperiodalignment: Optional[str] = Field(None, title="Xperiodalignment")
    marker_colors: Optional[List[str]] = Field(None, title="Marker Colors")
    textinfo: Optional[str] = Field(None, title="Textinfo")
    line: Optional[LineStyle] = Field(None, title="Line")


class WidgetType(str, Enum):
    plot = "plot"
    map = "map"
    text = "text"
    single_value = "single_value"


class WidgetSingleView(BaseModel):
    widget_type: WidgetType = Field(..., title="Widget Type")
    title: str = Field(..., title="Title")
    data: Union[Path, AnyUrl, str, int, float] = Field(..., title="Data")
    view: Optional[List[List]] = Field(None, title="View")


class LayoutStyle(BaseModel):
    font_color: Optional[str] = Field(None, title="Font Color")
    font_style: Optional[str] = Field(None, title="Font Style")
    plot_bgcolor: Optional[str] = Field(None, title="Plot Bgcolor")
    showlegend: Optional[bool] = Field(None, title="Showlegend")


class GroupedWidget(BaseModel):
    widget_type: WidgetType = Field(..., title="Widget Type")
    title: str = Field(..., title="Title")
    views: Dict[str, Union[Path, AnyUrl, str, int, float]] = Field(..., title="Views")


class Groupers(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    groupers: List[Grouper] = Field(
        ...,
        description="            Index(es) and/or column(s) to group by, along with\n            optional display names and help text.\n            ",
        title="Groupers",
    )


class FilterPatrolEvents(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    min_x: Optional[float] = Field(-180.0, title="Min X")
    max_x: Optional[float] = Field(180.0, title="Max X")
    min_y: Optional[float] = Field(-90.0, title="Min Y")
    max_y: Optional[float] = Field(90.0, title="Max Y")
    filter_point_coords: Optional[List[Coordinate]] = Field(
        default_factory=lambda: [
            Coordinate.model_validate(v) for v in [{"x": 0.0, "y": 0.0}]
        ],
        title="Filter Point Coords",
    )


class PeMapLayer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    layer_style: Union[PolylineLayerStyle, PolygonLayerStyle, PointLayerStyle] = Field(
        ..., description="Style arguments for the layer.", title="Layer Style"
    )
    legend: Optional[LegendDefinition] = Field(
        None,
        description="If present, includes this layer in the map legend",
        title="Legend",
    )


class PeEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layer: Optional[str] = Field(
        "", description="A named tile layer, ie OpenStreetMap.", title="Tile Layer"
    )
    static: Optional[bool] = Field(
        False, description="Set to true to disable map pan/zoom.", title="Static"
    )
    title: Optional[str] = Field("", description="The map title.", title="Title")
    north_arrow_style: Optional[NorthArrowStyle] = Field(
        default_factory=lambda: NorthArrowStyle.model_validate(
            {"placement": "top-left", "style": {"transform": "scale(0.8)"}}
        ),
        description="Additional arguments for configuring the North Arrow.",
        title="North Arrow Style",
    )
    legend_style: Optional[LegendStyle] = Field(
        default_factory=lambda: LegendStyle.model_validate(
            {"placement": "bottom-right"}
        ),
        description="Additional arguments for configuring the legend.",
        title="Legend Style",
    )


class FdMapLayer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    layer_style: Union[PolylineLayerStyle, PolygonLayerStyle, PointLayerStyle] = Field(
        ..., description="Style arguments for the layer.", title="Layer Style"
    )
    legend: Optional[LegendDefinition] = Field(
        None,
        description="If present, includes this layer in the map legend",
        title="Legend",
    )


class FdEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layer: Optional[str] = Field(
        "", description="A named tile layer, ie OpenStreetMap.", title="Tile Layer"
    )
    static: Optional[bool] = Field(
        False, description="Set to true to disable map pan/zoom.", title="Static"
    )
    title: Optional[str] = Field("", description="The map title.", title="Title")
    north_arrow_style: Optional[NorthArrowStyle] = Field(
        default_factory=lambda: NorthArrowStyle.model_validate(
            {"placement": "top-left", "style": {"transform": "scale(0.8)"}}
        ),
        description="Additional arguments for configuring the North Arrow.",
        title="North Arrow Style",
    )
    legend_style: Optional[LegendStyle] = Field(
        default_factory=lambda: LegendStyle.model_validate(
            {"placement": "bottom-right"}
        ),
        description="Additional arguments for configuring the legend.",
        title="Legend Style",
    )


class GroupedPeMapLayer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    layer_style: Union[PolylineLayerStyle, PolygonLayerStyle, PointLayerStyle] = Field(
        ..., description="Style arguments for the layer.", title="Layer Style"
    )
    legend: Optional[LegendDefinition] = Field(
        None,
        description="If present, includes this layer in the map legend",
        title="Legend",
    )


class GroupedPeEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layer: Optional[str] = Field(
        "", description="A named tile layer, ie OpenStreetMap.", title="Tile Layer"
    )
    static: Optional[bool] = Field(
        False, description="Set to true to disable map pan/zoom.", title="Static"
    )
    title: Optional[str] = Field("", description="The map title.", title="Title")
    north_arrow_style: Optional[NorthArrowStyle] = Field(
        default_factory=lambda: NorthArrowStyle.model_validate(
            {"placement": "top-left", "style": {"transform": "scale(0.8)"}}
        ),
        description="Additional arguments for configuring the North Arrow.",
        title="North Arrow Style",
    )
    legend_style: Optional[LegendStyle] = Field(
        default_factory=lambda: LegendStyle.model_validate(
            {"placement": "bottom-right"}
        ),
        description="Additional arguments for configuring the legend.",
        title="Legend Style",
    )


class GroupedPePieChart(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    value_column: str = Field(
        ...,
        description="The name of the dataframe column to pull slice values from.",
        title="Value Column",
    )
    label_column: Optional[str] = Field(
        None,
        description="The name of the dataframe column to label slices with, required if the data in value_column is numeric.",
        title="Label Column",
    )
    color_column: Optional[str] = Field(
        None,
        description="The name of the dataframe column to color slices with.",
        title="Color Column",
    )
    plot_style: Optional[PlotStyle] = Field(
        None,
        description="Additional style kwargs passed to go.Pie().",
        title="Plot Style",
    )
    layout_style: Optional[LayoutStyle] = Field(
        None,
        description="Additional kwargs passed to plotly.go.Figure(layout).",
        title="Layout Style",
    )


class GroupedFdMapLayer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    layer_style: Union[PolylineLayerStyle, PolygonLayerStyle, PointLayerStyle] = Field(
        ..., description="Style arguments for the layer.", title="Layer Style"
    )
    legend: Optional[LegendDefinition] = Field(
        None,
        description="If present, includes this layer in the map legend",
        title="Legend",
    )


class GroupedFdEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layer: Optional[str] = Field(
        "", description="A named tile layer, ie OpenStreetMap.", title="Tile Layer"
    )
    static: Optional[bool] = Field(
        False, description="Set to true to disable map pan/zoom.", title="Static"
    )
    title: Optional[str] = Field("", description="The map title.", title="Title")
    north_arrow_style: Optional[NorthArrowStyle] = Field(
        default_factory=lambda: NorthArrowStyle.model_validate(
            {"placement": "top-left", "style": {"transform": "scale(0.8)"}}
        ),
        description="Additional arguments for configuring the North Arrow.",
        title="North Arrow Style",
    )
    legend_style: Optional[LegendStyle] = Field(
        default_factory=lambda: LegendStyle.model_validate(
            {"placement": "bottom-right"}
        ),
        description="Additional arguments for configuring the legend.",
        title="Legend Style",
    )


class GroupedPlotStyle(BaseModel):
    category: str = Field(..., title="Category")
    plot_style: PlotCategoryStyle


class PeBarChart(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    x_axis: str = Field(
        ...,
        description="The dataframe column to plot in the x/time axis.",
        title="X Axis",
    )
    y_axis: str = Field(
        ..., description="The dataframe column to plot in the y axis.", title="Y Axis"
    )
    category: str = Field(
        ...,
        description="The dataframe column to stack in the y axis.",
        title="Category",
    )
    agg_function: AggFunction = Field(
        ...,
        description="The aggregate function to apply to the group.",
        title="Agg Function",
    )
    time_interval: TimeInterval = Field(
        ..., description="Sets the time interval of the x axis.", title="Time Interval"
    )
    color_column: Optional[str] = Field(
        None,
        description="The name of the dataframe column to color bars with.",
        title="Color Column",
    )
    grouped_styles: Optional[List[GroupedPlotStyle]] = Field(
        [],
        description="Style arguments passed to plotly.graph_objects.Bar and applied to individual groups.",
        title="Grouped Styles",
    )
    plot_style: Optional[PlotStyle] = Field(
        None,
        description="Additional style kwargs passed to go.Bar().",
        title="Plot Style",
    )
    layout_style: Optional[BarLayoutStyle] = Field(
        None,
        description="Additional kwargs passed to plotly.go.Figure(layout).",
        title="Layout Style",
    )


class Params(BaseModel):
    groupers: Optional[Groupers] = Field(None, title="Set Groupers")
    pe: Optional[Pe] = Field(None, title="Get Patrol Events from EarthRanger")
    filter_patrol_events: Optional[FilterPatrolEvents] = Field(
        None, title="Apply Relocation Coordinate Filter"
    )
    pe_add_temporal_index: Optional[PeAddTemporalIndex] = Field(
        None, title="Add temporal index to Patrol Events"
    )
    pe_colormap: Optional[PeColormap] = Field(None, title="Patrol Events Colormap")
    pe_map_layer: Optional[PeMapLayer] = Field(
        None, title="Create map layer from Patrol Events"
    )
    pe_ecomap: Optional[PeEcomap] = Field(None, title="Draw Ecomap from Time Density")
    pe_ecomap_html_url: Optional[PeEcomapHtmlUrl] = Field(
        None, title="Persist Ecomap as Text"
    )
    pe_map_widget: Optional[PeMapWidget] = Field(
        None, title="Create Time Density Map Widget"
    )
    pe_bar_chart: Optional[PeBarChart] = Field(
        None, title="Draw Time Series Bar Chart for Patrols Events"
    )
    pe_bar_chart_html_url: Optional[PeBarChartHtmlUrl] = Field(
        None, title="Persist Patrols Bar Chart as Text"
    )
    pe_bar_chart_widget: Optional[PeBarChartWidget] = Field(
        None, title="Create Plot Widget for Patrol Events"
    )
    pe_meshgrid: Optional[PeMeshgrid] = Field(
        None, title="Create Patrol Events Meshgrid"
    )
    pe_feature_density: Optional[PeFeatureDensity] = Field(
        None, title="Patrol Events Feature Density"
    )
    fd_colormap: Optional[FdColormap] = Field(None, title="Feature Density Colormap")
    fd_map_layer: Optional[FdMapLayer] = Field(
        None, title="Create map layer from Feature Density"
    )
    fd_ecomap: Optional[FdEcomap] = Field(
        None, title="Draw Ecomap from Feature Density"
    )
    fd_ecomap_html_url: Optional[FdEcomapHtmlUrl] = Field(
        None, title="Persist Feature Density Ecomap as Text"
    )
    fd_map_widget: Optional[FdMapWidget] = Field(
        None, title="Create Feature Density Map Widget"
    )
    split_patrol_event_groups: Optional[Dict[str, Any]] = Field(
        None, title="Split Patrol Events by Group"
    )
    grouped_pe_map_layer: Optional[GroupedPeMapLayer] = Field(
        None, title="Create map layer from grouped Patrol Events"
    )
    grouped_pe_ecomap: Optional[GroupedPeEcomap] = Field(
        None, title="Draw Ecomap from grouped Patrol Events"
    )
    grouped_pe_ecomap_html_url: Optional[GroupedPeEcomapHtmlUrl] = Field(
        None, title="Persist grouped Patrol Events Ecomap as Text"
    )
    grouped_pe_map_widget: Optional[GroupedPeMapWidget] = Field(
        None, title="Create grouped Patrol Events Map Widget"
    )
    grouped_pe_map_widget_merge: Optional[Dict[str, Any]] = Field(
        None, title="Merge Patrol Events Map Widget Views"
    )
    grouped_pe_pie_chart: Optional[GroupedPePieChart] = Field(
        None, title="Draw Pie Chart for Patrols Events"
    )
    grouped_pe_pie_chart_html_urls: Optional[GroupedPePieChartHtmlUrls] = Field(
        None, title="Persist Patrols Pie Chart as Text"
    )
    grouped_pe_pie_chart_widgets: Optional[GroupedPePieChartWidgets] = Field(
        None, title="Create Plot Widget for Patrol Events"
    )
    grouped_pe_pie_widget_merge: Optional[Dict[str, Any]] = Field(
        None, title="Merge Pie Chart Widget Views"
    )
    grouped_pe_feature_density: Optional[GroupedPeFeatureDensity] = Field(
        None, title="Grouped Patrol Events Feature Density"
    )
    grouped_fd_colormap: Optional[GroupedFdColormap] = Field(
        None, title="Grouped Feature Density Colormap"
    )
    grouped_fd_map_layer: Optional[GroupedFdMapLayer] = Field(
        None, title="Create map layer from Feature Density"
    )
    grouped_fd_ecomap: Optional[GroupedFdEcomap] = Field(
        None, title="Draw Ecomap from Feature Density"
    )
    grouped_fd_ecomap_html_url: Optional[GroupedFdEcomapHtmlUrl] = Field(
        None, title="Persist Feature Density Ecomap as Text"
    )
    grouped_fd_map_widget: Optional[GroupedFdMapWidget] = Field(
        None, title="Create Feature Density Map Widget"
    )
    grouped_fd_map_widget_merge: Optional[Dict[str, Any]] = Field(
        None, title="Merge Feature Density Widget Views"
    )
    patrol_dashboard: Optional[PatrolDashboard] = Field(
        None, title="Create Dashboard with Patrol Map Widgets"
    )
