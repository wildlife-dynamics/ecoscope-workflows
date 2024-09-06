from dataclasses import dataclass
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


class LayerStyleBase(BaseModel):
    auto_highlight: bool = False
    opacity: float = 1
    pickable: bool = True


class PolylineLayerStyle(LayerStyleBase):
    layer_type: Literal["polyline"] = Field("polyline", exclude=True)
    get_color: str | list[int] | list[list[int]] | None = None
    get_width: float = 1
    color_column: str | None = None


class ShapeLayerStyle(LayerStyleBase):
    filled: bool = True
    get_fill_color: str | list[int] | list[list[int]] | None = None
    get_line_color: str | list[int] | list[list[int]] | None = None
    get_line_width: float = 1
    fill_color_column: str | None = None
    line_color_column: str | None = None


class PointLayerStyle(ShapeLayerStyle):
    layer_type: Literal["point"] = Field("point", exclude=True)
    get_radius: float = 1


class PolygonLayerStyle(ShapeLayerStyle):
    layer_type: Literal["polygon"] = Field("polygon", exclude=True)
    extruded: bool = False
    get_elevation: float = 1000


LayerStyle = Annotated[
    Union[PolylineLayerStyle, PointLayerStyle, PolygonLayerStyle],
    Field(discriminator="layer_type"),
]


class NorthArrowStyle(BaseModel):
    placement: Literal[
        "top-left", "top-right", "bottom-left", "bottom-right", "fill"
    ] = "top-left"


@dataclass
class LayerDefinition:
    geodataframe: AnyGeoDataFrame
    layer_style: LayerStyle


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
    ] = None,
) -> Annotated[str, Field()]:
    """
    Creates a map based on the provided layer definitions and configuration.

    Args:
    geo_layers (LayerDefinition | list[LayerDefinition]): A list of map layers to add to the map.
    tile_layer (str): A named tile layer, ie OpenStreetMap.
    static (bool): Set to true to disable map pan/zoom.
    title (str): The map title.
    north_arrow_style (NorthArrowStyle): Additional arguments for configuring the North Arrow.

    Returns:
    str: A static HTML representation of the map.
    """

    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, default_widgets=False)

    if title:
        m.add_title(title)

    m.add_scale_bar()
    m.add_north_arrow(
        **(north_arrow_style.model_dump(exclude_none=True) if north_arrow_style else {})
    )

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

        m.add_layer(layer)

    m.zoom_to_bounds(m.layers)
    return m.to_html(title=title if title is not None else "Map Export")
