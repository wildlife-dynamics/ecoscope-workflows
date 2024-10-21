# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "8a3657e3ebaa4bfbe1bbaaac414f150f77aaa86dfa1e7d1d71c3b10235974666"


from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AnyUrl, AwareDatetime, BaseModel, ConfigDict, Field, confloat


class TimeRange(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    since: AwareDatetime = Field(..., description="The start time", title="Since")
    until: AwareDatetime = Field(..., description="The end time", title="Until")
    time_format: str = Field(..., description="The time format", title="Time Format")


class StatusEnum(str, Enum):
    active = "active"
    overdue = "overdue"
    done = "done"
    cancelled = "cancelled"


class PatrolObs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    patrol_type: List[str] = Field(
        ..., description="list of UUID of patrol types", title="Patrol Type"
    )
    status: List[StatusEnum] = Field(
        ...,
        description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'",
        title="Status",
    )
    include_patrol_details: Optional[bool] = Field(
        False, description="Include patrol details", title="Include Patrol Details"
    )


class PatrolTraj(BaseModel):
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


class PatrolEvents(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    patrol_type: List[str] = Field(
        ..., description="list of UUID of patrol types", title="Patrol Type"
    )
    status: List[str] = Field(
        ...,
        description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'",
        title="Status",
    )


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


class TrajPeEcomapHtmlUrls(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class TrajPeMapWidgetsSingleViews(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class TotalPatrols(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class TotalPatrolsSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class TotalPatrolsPerGroup(BaseModel):
    total_patrols: Optional[TotalPatrols] = Field(
        None, title="Calculate Total Patrols Per Group"
    )
    total_patrols_sv_widgets: Optional[TotalPatrolsSvWidgets] = Field(
        None, title="Create Single Value Widgets for Total Patrols Per Group"
    )
    total_patrols_grouped_sv_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Total Patrols SV widgets"
    )


class TotalPatrolTime(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class TotalPatrolTimeSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class TotalPatrolDist(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class TotalPatrolDistSvWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")
    decimal_places: Optional[int] = Field(
        1,
        description="The number of decimal places to display.",
        title="Decimal Places",
    )


class AvgSpeed(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    column_name: str = Field(
        ..., description="Column to aggregate", title="Column Name"
    )


class AvgSpeedSvWidgets(BaseModel):
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


class PatrolEventsBarChartHtmlUrl(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class PatrolEventsBarChartWidget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


class PePieChartHtmlUrls(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filename: Optional[str] = Field(
        None,
        description="            Optional filename to persist text to within the `root_path`.\n            If not provided, a filename will be generated based on a hash of the text content.\n            ",
        title="Filename",
    )


class PatrolEventsPieChartWidgets(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    title: str = Field(..., description="The title of the widget", title="Title")


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


class TimeRange1(BaseModel):
    since: AwareDatetime = Field(..., title="Since")
    until: AwareDatetime = Field(..., title="Until")
    time_format: Optional[str] = Field("%d %b %Y %H:%M:%S %Z", title="Time Format")


class Coordinate(BaseModel):
    x: float = Field(..., title="X")
    y: float = Field(..., title="Y")


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


class Unit(str, Enum):
    m = "m"
    km = "km"
    s = "s"
    h = "h"
    d = "d"
    m_s = "m/s"
    km_h = "km/h"


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


class LayoutStyle(BaseModel):
    font_color: Optional[str] = Field(None, title="Font Color")
    font_style: Optional[str] = Field(None, title="Font Style")
    plot_bgcolor: Optional[str] = Field(None, title="Plot Bgcolor")
    showlegend: Optional[bool] = Field(None, title="Showlegend")


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


class PatrolReloc(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    filter_point_coords: List[Coordinate] = Field(..., title="Filter Point Coords")
    relocs_columns: List[str] = Field(..., title="Relocs Columns")


class FetchAndPreprocessPatrolObservations(BaseModel):
    patrol_obs: Optional[PatrolObs] = Field(
        None, title="Get Patrol Observations from EarthRanger"
    )
    patrol_reloc: Optional[PatrolReloc] = Field(
        None, title="Transform Observations to Relocations"
    )
    patrol_traj: Optional[PatrolTraj] = Field(
        None, title="Transform Relocations to Trajectories"
    )
    traj_add_temporal_index: Optional[TrajAddTemporalIndex] = Field(
        None, title="Add temporal index to Patrol Trajectories"
    )


class PatrolTrajMapLayers(BaseModel):
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


class PatrolTrajectoriesMapLayers(BaseModel):
    split_patrol_traj_groups: Optional[Dict[str, Any]] = Field(
        None, title="Split Patrol Trajectories by Group"
    )
    patrol_traj_map_layers: Optional[PatrolTrajMapLayers] = Field(
        None, title="Create map layer for each Patrol Trajectories group"
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


class FetchAndPreprocessPatrolEvents(BaseModel):
    patrol_events: Optional[PatrolEvents] = Field(
        None, title="Get Patrol Events from EarthRanger"
    )
    filter_patrol_events: Optional[FilterPatrolEvents] = Field(
        None, title="Apply Relocation Coordinate Filter"
    )
    pe_add_temporal_index: Optional[PeAddTemporalIndex] = Field(
        None, title="Add temporal index to Patrol Events"
    )


class PatrolEventsMapLayers1(BaseModel):
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


class PatrolEventsMapLayers(BaseModel):
    pe_colormap: Optional[PeColormap] = Field(None, title="Patrol Events Colormap")
    split_pe_groups: Optional[Dict[str, Any]] = Field(
        None, title="Split Patrol Events by Group"
    )
    patrol_events_map_layers: Optional[PatrolEventsMapLayers1] = Field(
        None, title="Create map layers for each Patrols Events group"
    )


class TrajPatrolEventsEcomap(BaseModel):
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


class CombinedTrajectoriesAndPatrolEventsEcoMap(BaseModel):
    traj_patrol_events_ecomap: Optional[TrajPatrolEventsEcomap] = Field(
        None, title="Draw Ecomaps for each combined Trajectory and Patrol Events group"
    )
    traj_pe_ecomap_html_urls: Optional[TrajPeEcomapHtmlUrls] = Field(
        None, title="Persist Patrols Ecomap as Text"
    )
    traj_pe_map_widgets_single_views: Optional[TrajPeMapWidgetsSingleViews] = Field(
        None, title="Create Map Widgets for Patrol Events"
    )
    traj_pe_grouped_map_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge EcoMap Widget Views"
    )


class TotalPatrolTimeConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class TotalPatrolTimePerGroup(BaseModel):
    total_patrol_time: Optional[TotalPatrolTime] = Field(
        None, title="Calculate Total Patrol Time Per Group"
    )
    total_patrol_time_converted: Optional[TotalPatrolTimeConverted] = Field(
        None, title="Convert total patrol time units"
    )
    total_patrol_time_sv_widgets: Optional[TotalPatrolTimeSvWidgets] = Field(
        None, title="Create Single Value Widgets for Total Patrol Time Per Group"
    )
    patrol_time_grouped_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Total Patrol Time SV widgets"
    )


class TotalPatrolDistConverted(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    original_unit: Optional[Unit] = Field(
        None, description="The original unit of measurement.", title="Original Unit"
    )
    new_unit: Optional[Unit] = Field(
        None, description="The unit to convert to.", title="New Unit"
    )


class TotalDistancePerGroup(BaseModel):
    total_patrol_dist: Optional[TotalPatrolDist] = Field(
        None, title="Calculate Total Distance Per Group"
    )
    total_patrol_dist_converted: Optional[TotalPatrolDistConverted] = Field(
        None, title="Convert total patrol distance units"
    )
    total_patrol_dist_sv_widgets: Optional[TotalPatrolDistSvWidgets] = Field(
        None, title="Create Single Value Widgets for Total Distance Per Group"
    )
    patrol_dist_grouped_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Total Patrol Distance SV widgets"
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


class AverageSpeedPerGroup(BaseModel):
    avg_speed: Optional[AvgSpeed] = Field(
        None, title="Calculate Average Speed Per Group"
    )
    average_speed_converted: Optional[AverageSpeedConverted] = Field(
        None, title="Convert Average Speed units"
    )
    avg_speed_sv_widgets: Optional[AvgSpeedSvWidgets] = Field(
        None, title="Create Single Value Widgets for Avg Speed Per Group"
    )
    avg_speed_grouped_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Avg Speed SV widgets"
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


class MaxSpeedPerGroup(BaseModel):
    max_speed: Optional[MaxSpeed] = Field(None, title="Calculate Max Speed Per Group")
    max_speed_converted: Optional[MaxSpeedConverted] = Field(
        None, title="Convert Max Speed units"
    )
    max_speed_sv_widgets: Optional[MaxSpeedSvWidgets] = Field(
        None, title="Create Single Value Widgets for Max Speed Per Group"
    )
    max_speed_grouped_widget: Optional[Dict[str, Any]] = Field(
        None, title="Merge per group Max Speed SV widgets"
    )


class PatrolEventsPieChart1(BaseModel):
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


class PatrolEventsPieChart(BaseModel):
    patrol_events_pie_chart: Optional[PatrolEventsPieChart1] = Field(
        None, title="Draw Pie Chart for Patrols Events"
    )
    pe_pie_chart_html_urls: Optional[PePieChartHtmlUrls] = Field(
        None, title="Persist Patrols Pie Chart as Text"
    )
    patrol_events_pie_chart_widgets: Optional[PatrolEventsPieChartWidgets] = Field(
        None, title="Create Plot Widget for Patrol Events"
    )
    patrol_events_pie_widget_grouped: Optional[Dict[str, Any]] = Field(
        None, title="Merge Pie Chart Widget Views"
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


class TimeDensityMap(BaseModel):
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


class Quantity(BaseModel):
    value: Union[int, float] = Field(..., title="Value")
    unit: Optional[Unit] = None


class GroupedPlotStyle(BaseModel):
    category: str = Field(..., title="Category")
    plot_style: PlotCategoryStyle


class PatrolEventsBarChart1(BaseModel):
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


class PatrolEventsBarChart(BaseModel):
    patrol_events_bar_chart: Optional[PatrolEventsBarChart1] = Field(
        None, title="Draw Time Series Bar Chart for Patrols Events"
    )
    patrol_events_bar_chart_html_url: Optional[PatrolEventsBarChartHtmlUrl] = Field(
        None, title="Persist Patrols Bar Chart as Text"
    )
    patrol_events_bar_chart_widget: Optional[PatrolEventsBarChartWidget] = Field(
        None, title="Create Plot Widget for Patrol Events"
    )


class FormData(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    groupers: Optional[Groupers] = Field(None, title="Set Groupers")
    time_range: Optional[TimeRange] = Field(None, title="Set Time Range Filters")
    Fetch_and_preprocess_patrol_observations: Optional[
        FetchAndPreprocessPatrolObservations
    ] = Field(
        None,
        alias="Fetch and preprocess patrol observations",
        description="Fetch patrol observations from EarthRanger, preprocess them into trajectories, and add a temporal index.",
    )
    Patrol_trajectories_map_layers: Optional[PatrolTrajectoriesMapLayers] = Field(
        None,
        alias="Patrol trajectories map layers",
        description="Create map layers for each group of patrol trajectories.",
    )
    Fetch_and_preprocess_patrol_events: Optional[FetchAndPreprocessPatrolEvents] = (
        Field(
            None,
            alias="Fetch and preprocess patrol events",
            description="Fetch patrol events from EarthRanger, filter them, and add a temporal index.",
        )
    )
    Patrol_events_map_layers: Optional[PatrolEventsMapLayers] = Field(
        None,
        alias="Patrol events map layers",
        description="Create map layers for each group of patrol events.",
    )
    combined_traj_and_pe_map_layers: Optional[Dict[str, Any]] = Field(
        None, title="Combine Trajectories and Patrol Events layers"
    )
    Combined_Trajectories_and_Patrol_Events_EcoMap: Optional[
        CombinedTrajectoriesAndPatrolEventsEcoMap
    ] = Field(
        None,
        alias="Combined Trajectories and Patrol Events EcoMap",
        description="Draw EcoMaps for each combined Trajectory and Patrol Events group.",
    )
    Total_patrols_per_group: Optional[TotalPatrolsPerGroup] = Field(
        None,
        alias="Total patrols per group",
        description="Create a single value widget for the total patrols per group.",
    )
    Total_patrol_time_per_group: Optional[TotalPatrolTimePerGroup] = Field(
        None,
        alias="Total patrol time per group",
        description="Create a single value widget for the total patrol time per group.",
    )
    Total_distance_per_group: Optional[TotalDistancePerGroup] = Field(
        None,
        alias="Total distance per group",
        description="Create a single value widget for the total distance per group.",
    )
    Average_speed_per_group: Optional[AverageSpeedPerGroup] = Field(
        None,
        alias="Average speed per group",
        description="Create a single value widget for the average speed per group.",
    )
    Max_speed_per_group: Optional[MaxSpeedPerGroup] = Field(
        None,
        alias="Max speed per group",
        description="Create a single value widget for the max speed per group.",
    )
    Patrol_events_bar_chart: Optional[PatrolEventsBarChart] = Field(
        None,
        alias="Patrol events bar chart",
        description="Create the patrol events bar chart.",
    )
    Patrol_events_pie_chart: Optional[PatrolEventsPieChart] = Field(
        None,
        alias="Patrol events pie chart",
        description="Create the patrol events pie chart.",
    )
    Time_Density_Map: Optional[TimeDensityMap] = Field(
        None,
        alias="Time Density Map",
        description="Calculate time density from patrol trajectories and display it on a map.",
    )
    patrol_dashboard: Optional[PatrolDashboard] = Field(
        None, title="Create Dashboard with Patrol Map Widgets"
    )
