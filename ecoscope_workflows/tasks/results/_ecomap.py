from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


class LayerStyleProperty(BaseModel):
    auto_highlight: bool = False
    opacity: float = 1
    pickable: bool = True


class PolylineLayerProperty(LayerStyleProperty):
    get_color: list[int] = [0, 0, 0, 255]
    get_width: float = 1


class ShapeLayerProperty(LayerStyleProperty):
    filled: bool = True
    get_fill_color: list[int] = [0, 0, 0, 255]
    get_line_color: list[int] = [0, 0, 0, 255]
    get_line_width: float = 1


class PointLayerProperty(ShapeLayerProperty):
    get_radius: float = 1


class PolygonLayerProperty(ShapeLayerProperty):
    extruded: bool = False
    get_elevation: float = 1000


@dataclass
class LayerDefinition:
    geodataframe: AnyGeoDataFrame
    style_kws: LayerStyleProperty


@task
def create_map_layer(
    geodataframe: Annotated[
        AnyGeoDataFrame,
        Field(description="The geodataframe to visualize.", exclude=True),
    ],
    layer_style: Annotated[
        PolylineLayerProperty | PolygonLayerProperty | PointLayerProperty,
        Field(description="Style arguments for the layer."),
    ],
) -> Annotated[LayerDefinition, Field()]:
    """
    Creates a map layer definition based on the provided configuration.

    Args:
    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.
    style_kws (dict): Style arguments for the data visualization.

    Returns:
    The generated LayerDefinition
    """

    return LayerDefinition(
        geodataframe=geodataframe,
        style_kws=layer_style,
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
    title_kws: Annotated[
        dict | SkipJsonSchema[None],
        Field(description="Additional arguments for configuring the Title."),
    ] = None,
    scale_kws: Annotated[
        dict | SkipJsonSchema[None],
        Field(description="Additional arguments for configuring the Scale Bar."),
    ] = None,
    north_arrow_kws: Annotated[
        dict | SkipJsonSchema[None],
        Field(description="Additional arguments for configuring the North Arrow."),
    ] = None,
) -> Annotated[str, Field()]:
    """
    Creates a map based on the provided layer definitions and configuration.

    Args:
    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.
    data_type (str): The type of visualization, "Scatterplot", "Path" or "Polygon".
    style_kws (dict): Style arguments for the data visualization.
    tile_layer (str): A named tile layer, ie OpenStreetMap.
    static (bool): Set to true to disable map pan/zoom.
    title (str): The map title.
    title_kws (dict): Additional arguments for configuring the Title.
    scale_kws (dict): Additional arguments for configuring the Scale Bar.
    north_arrow_kws (dict): Additional arguments for configuring the North Arrow.

    Returns:
    str: A static HTML representation of the map.
    """

    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, default_widgets=False)

    if title:
        m.add_title(title, **(title_kws or {}))

    m.add_scale_bar(**(scale_kws or {}))
    m.add_north_arrow(**(north_arrow_kws or {}))

    if tile_layer:
        m.add_layer(EcoMap.get_named_tile_layer(tile_layer))

    geo_layers = [geo_layers] if not isinstance(geo_layers, list) else geo_layers
    for layer_def in geo_layers:
        if isinstance(layer_def.style_kws, PolylineLayerProperty):
            layer = EcoMap.polyline_layer(
                layer_def.geodataframe, **layer_def.style_kws.model_dump()
            )
        elif isinstance(layer_def.style_kws, PointLayerProperty):
            layer = EcoMap.point_layer(
                layer_def.geodataframe, **layer_def.style_kws.model_dump()
            )
        elif isinstance(layer_def, PolygonLayerProperty):
            layer = EcoMap.polygon_layer(
                layer_def.geodataframe, **layer_def.style_kws.model_dump()
            )

        m.add_layer(layer)

    m.zoom_to_bounds(m.layers)
    return m.to_html(title=title if title is not None else "Map Export")
