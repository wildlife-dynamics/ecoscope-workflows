# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "7875a291d3f7b77206919e350fd5dedb11be8260f09bdf5203901ac61ca53c16"


from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AnyUrl, AwareDatetime, BaseModel, ConfigDict, Field


class TimeRange(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    since: AwareDatetime = Field(..., description="The start time", title="Since")
    until: AwareDatetime = Field(..., description="The end time", title="Until")
    time_format: str = Field(..., description="The time format", title="Time Format")


class SubjectObs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    subject_group_name: str = Field(
        ..., description="Name of EarthRanger Subject", title="Subject Group Name"
    )
    include_inactive: Optional[bool] = Field(
        True,
        description="Whether or not to include inactive subjects",
        title="Include Inactive",
    )


class SubjectTraj(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    min_length_meters: Optional[float] = Field(0.1, title="Min Length Meters")
    max_length_meters: Optional[float] = Field(10000, title="Max Length Meters")
    max_time_secs: Optional[float] = Field(3600, title="Max Time Secs")
    min_time_secs: Optional[float] = Field(1, title="Min Time Secs")
    max_speed_kmhr: Optional[float] = Field(120, title="Max Speed Kmhr")
    min_speed_kmhr: Optional[float] = Field(0.0, title="Min Speed Kmhr")


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


class TrajAddTemporalIndex(BaseModel):
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


class ColormapTrajSpeed(BaseModel):
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


class EcomapHtmlUrls(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class TrajMapWidgetsSingleViews(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class ColormapTrajNight(BaseModel):
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


class EcomapDaynightHtmlUrls(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class TrajMapDaynightWidgetsSv(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class MeanSpeed(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class MeanSpeedSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class MaxSpeed(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class MaxSpeedSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class NumLocationSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class DaynightRatioSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class TotalDistance(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class TotalDistanceSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class TotalTime(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class TotalTimeSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class Td(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    pixel_size: Optional[float] = Field(
        250.0, description="Pixel size for raster profile.", title="Pixel Size"
    )
    crs: Optional[str] = Field("ESRI:102022", title="Crs")
    nodata_value: Optional[Union[float, str]] = Field("nan", title="Nodata Value")
    band_count: Optional[int] = Field(1, title="Band Count")
    max_speed_factor: Optional[float] = Field(1.05, title="Max Speed Factor")
    expansion_factor: Optional[float] = Field(1.3, title="Expansion Factor")
    percentiles: Optional[List[float]] = Field(
        [50.0, 60.0, 70.0, 80.0, 90.0, 95.0], title="Percentiles"
    )


class TdColormap(BaseModel):
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


class TdEcomapHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class TdMapWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class NsdChartHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class NsdChartWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class SubjectTrackingDashboard(BaseModel):
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


class TimeRange1(BaseModel):
    since: AwareDatetime = Field(..., title="Since")
    until: AwareDatetime = Field(..., title="Until")
    time_format: Optional[str] = Field("%d %b %Y %H:%M:%S %Z", title="Time Format")


class Coordinate(BaseModel):
    x: float = Field(..., title="X")
    y: float = Field(..., title="Y")


class Scheme(str, Enum):
    equal_interval = "equal_interval"
    quantile = "quantile"
    fisher_jenks = "fisher_jenks"
    std_mean = "std_mean"
    max_breaks = "max_breaks"
    natural_breaks = "natural_breaks"


class FisherJenksArgs(BaseModel):
    scheme: Optional[Scheme] = Field("fisher_jenks", title="Scheme")
    k: Optional[int] = Field(5, title="K")


class MaxBreaksArgs(BaseModel):
    scheme: Optional[Scheme] = Field("max_breaks", title="Scheme")
    k: Optional[int] = Field(5, title="K")
    mindiff: Optional[float] = Field(0, title="Mindiff")


class NaturalBreaksArgs(BaseModel):
    scheme: Optional[Scheme] = Field("natural_breaks", title="Scheme")
    k: Optional[int] = Field(5, title="K")
    initial: Optional[int] = Field(10, title="Initial")


class QuantileArgs(BaseModel):
    scheme: Optional[Scheme] = Field("quantile", title="Scheme")
    k: Optional[int] = Field(5, title="K")


class SharedArgs(BaseModel):
    scheme: Optional[Scheme] = Field("equal_interval", title="Scheme")
    k: Optional[int] = Field(5, title="K")


class StdMeanArgs(BaseModel):
    scheme: Optional[Scheme] = Field("std_mean", title="Scheme")
    multiples: Optional[List[int]] = Field([-2, -1, 1, 2], title="Multiples")
    anchor: Optional[bool] = Field(False, title="Anchor")


class Unit(str, Enum):
    m = "m"
    km = "km"
    s = "s"
    h = "h"
    d = "d"
    m_s = "m/s"
    km_h = "km/h"


class LegendDefinition(BaseModel):
    label_column: Optional[str] = Field(None, title="Label Column")
    color_column: Optional[str] = Field(None, title="Color Column")
    labels: Optional[List[str]] = Field(None, title="Labels")
    colors: Optional[List[str]] = Field(None, title="Colors")


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
    get_radius: Optional[float] = Field(5, title="Get Radius")
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
    get_width: Optional[float] = Field(3, title="Get Width")
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


class TileLayer(BaseModel):
    name: str = Field(..., title="Name")
    opacity: Optional[float] = Field(1, title="Opacity")


class WidgetType(str, Enum):
    graph = "graph"
    map = "map"
    text = "text"
    stat = "stat"


class WidgetSingleView(BaseModel):
    widget_type: WidgetType = Field(..., title="Widget Type")
    title: str = Field(..., title="Title")
    is_filtered: bool = Field(..., title="Is Filtered")
    data: Union[Path, AnyUrl, str] = Field(..., title="Data")
    view: Optional[List[List]] = Field(None, title="View")


class Quantity(BaseModel):
    value: Union[int, float] = Field(..., title="Value")
    unit: Optional[Unit] = None


class LineStyle(BaseModel):
    color: Optional[str] = Field(None, title="Color")


class PlotStyle(BaseModel):
    xperiodalignment: Optional[str] = Field(None, title="Xperiodalignment")
    marker_colors: Optional[List[str]] = Field(None, title="Marker Colors")
    textinfo: Optional[str] = Field(None, title="Textinfo")
    line: Optional[LineStyle] = Field(None, title="Line")


class GroupedWidget(BaseModel):
    widget_type: WidgetType = Field(..., title="Widget Type")
    title: str = Field(..., title="Title")
    is_filtered: bool = Field(..., title="Is Filtered")
    views: Dict[str, Union[Path, AnyUrl, str]] = Field(..., title="Views")


class Groupers(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    groupers: List[Grouper] = Field(
        ...,
        description="            Index(es) and/or column(s) to group by, along with\n            optional display names and help text.\n            ",
        title="Groupers",
    )


class SubjectReloc(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filter_point_coords: List[Coordinate] = Field(..., title="Filter Point Coords")
    relocs_columns: List[str] = Field(..., title="Relocs Columns")


class ClassifyTrajSpeed(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    input_column_name: str = Field(
        ..., description="The dataframe column to classify.", title="Input Column Name"
    )
    output_column_name: Optional[str] = Field(
        None,
        description="The dataframe column that will contain the classification values.",
        title="Output Column Name",
    )
    labels: Optional[List[str]] = Field(
        None,
        description="Labels of classification bins, uses bin edges if not provied.",
        title="Labels",
    )
    classification_options: Optional[
        Union[
            SharedArgs,
            StdMeanArgs,
            MaxBreaksArgs,
            NaturalBreaksArgs,
            QuantileArgs,
            FisherJenksArgs,
        ]
    ] = Field({"k": 5}, title="Classification Options")


class SpeedmapLegendWithUnit(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    input_column_name: str = Field(
        ..., description="The column name to map.", title="Input Column Name"
    )
    output_column_name: str = Field(
        ..., description="The new column name.", title="Output Column Name"
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class TrajMapLayers(BaseModel):
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


class TrajEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layers: Optional[List[TileLayer]] = Field(
        [],
        description="A list of named tile layer with opacity, ie OpenStreetMap.",
        title="Tile Layers",
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


class TrajMapNightLayers(BaseModel):
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


class TrajDaynightEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layers: Optional[List[TileLayer]] = Field(
        [],
        description="A list of named tile layer with opacity, ie OpenStreetMap.",
        title="Tile Layers",
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


class AverageSpeedConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class MaxSpeedConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class TotalDistConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class TotalTimeConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class TdMapLayer(BaseModel):
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


class TdEcomap(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    tile_layers: Optional[List[TileLayer]] = Field(
        [],
        description="A list of named tile layer with opacity, ie OpenStreetMap.",
        title="Tile Layers",
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


class NsdChart(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    group_by: str = Field(
        ..., description="The dataframe column to group by.", title="Group By"
    )
    x_axis: str = Field(
        ..., description="The dataframe column to plot in the x axis.", title="X Axis"
    )
    y_axis: str = Field(
        ..., description="The dataframe column to plot in the y axis.", title="Y Axis"
    )
    plot_style: Optional[PlotStyle] = Field(
        None,
        description="Style arguments passed to plotly.graph_objects.Scatter.",
        title="Plot Style",
    )
    color_column: Optional[str] = Field(
        None,
        description="The name of the dataframe column to color each plot group with.",
        title="Color Column",
    )


class FormData(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    groupers: Optional[Groupers] = Field(None, title="Set Groupers")
    time_range: Optional[TimeRange] = Field(None, title="Set Time Range Filters")
    subject_obs: Optional[SubjectObs] = Field(
        None, title="Get Subject Group Observations from EarthRanger"
    )
    subject_reloc: Optional[SubjectReloc] = Field(
        None, title="Transform Observations to Relocations"
    )
    day_night_labels: Optional[Dict[str, Any]] = Field(
        None, title="Apply Day/Night Labels to Relocations"
    )
    subject_traj: Optional[SubjectTraj] = Field(
        None, title="Transform Relocations to Trajectories"
    )
    traj_add_temporal_index: Optional[TrajAddTemporalIndex] = Field(
        None, title="Add temporal index to Subject Trajectories"
    )
    split_subject_traj_groups: Optional[Dict[str, Any]] = Field(
        None, title="Split Subject Trajectories by Group"
    )
    classify_traj_speed: Optional[ClassifyTrajSpeed] = Field(
        None, title="Classify Trajectories By Speed"
    )
    colormap_traj_speed: Optional[ColormapTrajSpeed] = Field(
        None, title="Apply Color to Trajectories By Speed"
    )
    speedmap_legend_with_unit: Optional[SpeedmapLegendWithUnit] = Field(
        None, title="Format Speedmap Legend Label"
    )
    traj_map_layers: Optional[TrajMapLayers] = Field(
        None, title="Create map layer for each trajectory group"
    )
    traj_ecomap: Optional[TrajEcomap] = Field(
        None, title="Draw Ecomaps for each trajectory group"
    )
    ecomap_html_urls: Optional[EcomapHtmlUrls] = Field(
        None, title="Persist ecomap as Text"
    )
    traj_map_widgets_single_views: Optional[TrajMapWidgetsSingleViews] = Field(
        None, title="Create Map Widgets for Trajectories"
    )
    traj_grouped_map_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge EcoMap Widget Views"
    )
    colormap_traj_night: Optional[ColormapTrajNight] = Field(
        None, title="Apply Color to Trajectories By Day/Night"
    )
    traj_map_night_layers: Optional[TrajMapNightLayers] = Field(
        None, title="Create map layer for each trajectory group"
    )
    traj_daynight_ecomap: Optional[TrajDaynightEcomap] = Field(
        None, title="Draw Ecomaps for each trajectory group"
    )
    ecomap_daynight_html_urls: Optional[EcomapDaynightHtmlUrls] = Field(
        None, title="Persist ecomap as Text"
    )
    traj_map_daynight_widgets_sv: Optional[TrajMapDaynightWidgetsSv] = Field(
        None, title="Create Map Widgets for Trajectories"
    )
    traj_daynight_grouped_map_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge EcoMap Widget Views"
    )
    mean_speed: Optional[MeanSpeed] = Field(
        None, title="Calculate Mean Speed Per Group"
    )
    average_speed_converted: Optional[AverageSpeedConverted] = Field(
        None, title="Convert Average Speed units"
    )
    mean_speed_sv_widgets: Optional[MeanSpeedSvWidgets] = Field(
        None, title="Create Single Value Widgets for Mean Speed Per Group"
    )
    mean_speed_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Mean Speed SV widgets"
    )
    max_speed: Optional[MaxSpeed] = Field(None, title="Calculate Max Speed Per Group")
    max_speed_converted: Optional[MaxSpeedConverted] = Field(
        None, title="Convert Max Speed units"
    )
    max_speed_sv_widgets: Optional[MaxSpeedSvWidgets] = Field(
        None, title="Create Single Value Widgets for Max Speed Per Group"
    )
    max_speed_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Max Speed SV widgets"
    )
    num_location: Optional[Dict[str, Any]] = Field(
        None, title="Calculate Number of Locations Per Group"
    )
    num_location_sv_widgets: Optional[NumLocationSvWidgets] = Field(
        None, title="Create Single Value Widgets for Number of Location Per Group"
    )
    num_location_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Number of Locations SV widgets"
    )
    daynight_ratio: Optional[Dict[str, Any]] = Field(
        None, title="Calculate Day/Night Ratio Per Group"
    )
    daynight_ratio_sv_widgets: Optional[DaynightRatioSvWidgets] = Field(
        None, title="Create Single Value Widgets for Day/Night Ratio Per Group"
    )
    daynight_ratio_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Day/Night Ratio SV widgets"
    )
    total_distance: Optional[TotalDistance] = Field(
        None, title="Calculate Total Distance Per Group"
    )
    total_dist_converted: Optional[TotalDistConverted] = Field(
        None, title="Convert total distance units"
    )
    total_distance_sv_widgets: Optional[TotalDistanceSvWidgets] = Field(
        None, title="Create Single Value Widgets for Total Distance Per Group"
    )
    total_dist_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Total Distance SV widgets"
    )
    total_time: Optional[TotalTime] = Field(
        None, title="Calculate Total Time Per Group"
    )
    total_time_converted: Optional[TotalTimeConverted] = Field(
        None, title="Convert total time units"
    )
    total_time_sv_widgets: Optional[TotalTimeSvWidgets] = Field(
        None, title="Create Single Value Widgets for Total Distance Per Group"
    )
    total_time_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Total Distance SV widgets"
    )
    td: Optional[Td] = Field(None, title="Calculate Time Density from Trajectory")
    td_colormap: Optional[TdColormap] = Field(None, title="Time Density Colormap")
    td_map_layer: Optional[TdMapLayer] = Field(
        None, title="Create map layer from Time Density"
    )
    td_ecomap: Optional[TdEcomap] = Field(None, title="Draw Ecomap from Time Density")
    td_ecomap_html_url: Optional[TdEcomapHtmlUrl] = Field(
        None, title="Persist Ecomap as Text"
    )
    td_map_widget: Optional[TdMapWidget] = Field(
        None, title="Create Time Density Map Widget"
    )
    td_grouped_map_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge Time Density Map Widget Views"
    )
    nsd_chart: Optional[NsdChart] = Field(None, title="Draw NSD Scatter Chart")
    nsd_chart_html_url: Optional[NsdChartHtmlUrl] = Field(
        None, title="Persist NSD Scatter Chart as Text"
    )
    nsd_chart_widget: Optional[NsdChartWidget] = Field(
        None, title="Create NSD Plot Widget"
    )
    subject_tracking_dashboard: Optional[SubjectTrackingDashboard] = Field(
        None, title="Create Dashboard with Subject Tracking Widgets"
    )
