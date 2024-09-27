# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "b0fa76dad8c1bfe3f9f93cb3c0c30bb03e02beacd4cc3e802bc61d26f1203024"


from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ObsA(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    subject_group_name: str = Field(
        ..., description="Name of EarthRanger Subject", title="Subject Group Name"
    )
    since: AwareDatetime = Field(..., description="Start date", title="Since")
    until: AwareDatetime = Field(..., description="End date", title="Until")
    include_inactive: Optional[bool] = Field(
        True,
        description="Whether or not to include inactive subjects",
        title="Include Inactive",
    )


class ObsB(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    subject_group_name: str = Field(
        ..., description="Name of EarthRanger Subject", title="Subject Group Name"
    )
    since: AwareDatetime = Field(..., description="Start date", title="Since")
    until: AwareDatetime = Field(..., description="End date", title="Until")
    include_inactive: Optional[bool] = Field(
        True,
        description="Whether or not to include inactive subjects",
        title="Include Inactive",
    )


class ObsC(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    client: str = Field(
        ..., description="A named EarthRanger connection.", title="Client"
    )
    subject_group_name: str = Field(
        ..., description="Name of EarthRanger Subject", title="Subject Group Name"
    )
    since: AwareDatetime = Field(..., description="Start date", title="Since")
    until: AwareDatetime = Field(..., description="End date", title="Until")
    include_inactive: Optional[bool] = Field(
        True,
        description="Whether or not to include inactive subjects",
        title="Include Inactive",
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


class MapLayers(BaseModel):
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


class Ecomaps(BaseModel):
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


class Params(BaseModel):
    obs_a: Optional[ObsA] = Field(None, title="Get Observations A")
    obs_b: Optional[ObsB] = Field(None, title="Get Observations B")
    obs_c: Optional[ObsC] = Field(None, title="Get Observations C")
    map_layers: Optional[MapLayers] = Field(
        None, title="Create Map Layer For Each Group"
    )
    ecomaps: Optional[Ecomaps] = Field(None, title="Create EcoMap For Each Group")
    td_ecomap_html_url: Optional[TdEcomapHtmlUrl] = Field(
        None, title="Persist Ecomaps as Text"
    )
