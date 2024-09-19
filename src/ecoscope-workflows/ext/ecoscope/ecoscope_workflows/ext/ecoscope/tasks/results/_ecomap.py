from dataclasses import dataclass
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows.core.annotations import AnyGeoDataFrame
from ecoscope_workflows.core.decorators import task


UnitType = Literal["meters", "pixels"]
WidgetPlacement = Literal[
    "top-left", "top-right", "bottom-left", "bottom-right", "fill"
]


class LayerStyleBase(BaseModel):
    auto_highlight: bool = False
    opacity: float = 1
    pickable: bool = True


class PolylineLayerStyle(LayerStyleBase):
    layer_type: Literal["polyline"] = Field("polyline", exclude=True)
    get_color: str | list[int] | list[list[int]] | None = None
    get_width: float = 1
    color_column: str | None = None
    width_units: UnitType = "pixels"
    cap_rounded: bool = True


class ShapeLayerStyle(LayerStyleBase):
    filled: bool = True
    get_fill_color: str | list[int] | list[list[int]] | None = None
    get_line_color: str | list[int] | list[list[int]] | None = None
    get_line_width: float = 1
    fill_color_column: str | None = None
    line_width_units: UnitType = "pixels"


class PointLayerStyle(ShapeLayerStyle):
    layer_type: Literal["point"] = Field("point", exclude=True)
    get_radius: float = 1
    radius_units: UnitType = "pixels"


class PolygonLayerStyle(ShapeLayerStyle):
    layer_type: Literal["polygon"] = Field("polygon", exclude=True)
    extruded: bool = False
    get_elevation: float = 1000


LayerStyle = Annotated[
    Union[PolylineLayerStyle, PointLayerStyle, PolygonLayerStyle],
    Field(discriminator="layer_type"),
]


class NorthArrowStyle(BaseModel):
    placement: WidgetPlacement = "top-left"
    style: dict = {"transform": "scale(0.8)"}


class LegendStyle(BaseModel):
    placement: WidgetPlacement = "bottom-right"


@dataclass
class LegendDefinition:
    label_column: str
    color_column: str


@dataclass
class LayerDefinition:
    geodataframe: AnyGeoDataFrame
    layer_style: LayerStyle
    legend: LegendDefinition


@task
def create_map_layer(
    geodataframe: Annotated[
        AnyGeoDataFrame,
        Field(description="The geodataframe to visualize.", exclude=True),
    ],
    layer_style: Annotated[
        PolylineLayerStyle | PolygonLayerStyle | PointLayerStyle,
        Field(description="Style arguments for the layer."),
    ],
    legend: Annotated[
        LegendDefinition | SkipJsonSchema[None],
        Field(description="If present, includes this layer in the map legend"),
    ] = None,
) -> Annotated[LayerDefinition, Field()]:
    """
    Creates a map layer definition based on the provided configuration.

    Args:
    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.
    layer_style (LayerStyle): Style arguments for the data visualization.

    Returns:
    The generated LayerDefinition
    """

    return LayerDefinition(
        geodataframe=geodataframe,
        layer_style=layer_style,
        legend=legend,  # type: ignore[arg-type]
    )


@task
def draw_ecomap(
    geo_layers: Annotated[
        LayerDefinition | list[LayerDefinition],
        Field(description="A list of map layers to add to the map.", exclude=True),
    ],
    tile_layer: Annotated[
        str, Field(description="A named tile layer, ie OpenStreetMap.")
    ] = "",
    static: Annotated[
        bool, Field(description="Set to true to disable map pan/zoom.")
    ] = False,
    title: Annotated[str, Field(description="The map title.")] = "",
    north_arrow_style: Annotated[
        NorthArrowStyle | SkipJsonSchema[None],
        Field(description="Additional arguments for configuring the North Arrow."),
    ] = NorthArrowStyle(),
    legend_style: Annotated[
        LegendStyle | SkipJsonSchema[None],
        Field(description="Additional arguments for configuring the legend."),
    ] = LegendStyle(),
) -> Annotated[str, Field()]:
    """
    Creates a map based on the provided layer definitions and configuration.

    Args:
    geo_layers (LayerDefinition | list[LayerDefinition]): A list of map layers to add to the map.
    tile_layer (str): A named tile layer, ie OpenStreetMap.
    static (bool): Set to true to disable map pan/zoom.
    title (str): The map title.
    north_arrow_style (NorthArrowStyle): Additional arguments for configuring the North Arrow.
    legend_style (WidgetStyleBase): Additional arguments for configuring the Legend.

    Returns:
    str: A static HTML representation of the map.
    """

    from ecoscope.mapping import EcoMap  # type: ignore[import-untyped]

    legend_labels: list = []
    legend_colors: list = []

    m = EcoMap(static=static, default_widgets=False)

    if title:
        m.add_title(title)

    m.add_scale_bar()
    m.add_north_arrow(**(north_arrow_style.model_dump(exclude_none=True)))  # type: ignore[union-attr]

    if tile_layer:
        m.add_layer(EcoMap.get_named_tile_layer(tile_layer))

    geo_layers = [geo_layers] if not isinstance(geo_layers, list) else geo_layers
    for layer_def in geo_layers:
        match layer_def.layer_style.layer_type:
            case "point":
                layer = EcoMap.point_layer(
                    layer_def.geodataframe,
                    **layer_def.layer_style.model_dump(exclude_none=True),
                )
            case "polyline":
                layer = EcoMap.polyline_layer(
                    layer_def.geodataframe,
                    **layer_def.layer_style.model_dump(exclude_none=True),
                )
            case "polygon":
                layer = EcoMap.polygon_layer(
                    layer_def.geodataframe,
                    **layer_def.layer_style.model_dump(exclude_none=True),
                )

        if layer_def.legend:
            legend_labels.extend(layer_def.geodataframe[layer_def.legend.label_column])
            legend_colors.extend(layer_def.geodataframe[layer_def.legend.color_column])

        m.add_layer(layer)

    if len(legend_labels) > 0:
        m.add_legend(
            labels=legend_labels,
            colors=[str(lc) for lc in legend_colors],
            **(legend_style.model_dump(exclude_none=True)),  # type: ignore[union-attr]
        )

    m.zoom_to_bounds(m.layers)
    return m.to_html(title=title if title is not None else "Map Export")
