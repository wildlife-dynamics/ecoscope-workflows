from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import distributed


@distributed
def create_map_layer(
    geodataframe: Annotated[
        AnyGeoDataFrame, Field(description="The geodataframe to visualize.")
    ],
    data_type: Annotated[
        Literal["Point", "Polyline", "Polygon"],
        Field(description="The type of visualization."),
    ],
    style_kws: Annotated[dict, Field(description="Style arguments for the layer.")],
) -> Annotated[object, Field()]:
    """
    Creates a map layer based on the provided configuration.

    Args:
    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.
    data_type (str): The type of visualization, "Scatterplot", "Path" or "Polygon".
    style_kws (dict): Style arguments for the data visualization.

    Returns:
    The generated map layer
    """

    from ecoscope.mapping import EcoMap

    match data_type:
        case "Point":
            layer = EcoMap.point_layer(geodataframe, **style_kws)
        case "Polyline":
            layer = EcoMap.polyline_layer(geodataframe, **style_kws)
        case "Polygon":
            layer = EcoMap.polygon_layer(geodataframe, **style_kws)

    return layer


@distributed
def draw_ecomap(
    geo_layers: Annotated[
        list[object], Field(description="A list of map layers to add to the map.")
    ],
    tile_layer: Annotated[
        str, Field(description="A named tile layer, ie OpenStreetMap.")
    ] = "",
    static: Annotated[
        bool, Field(description="Set to true to disable map pan/zoom.")
    ] = False,
    title: Annotated[str, Field(description="The map title.")] = "",
    title_kws: Annotated[
        dict, Field(description="Additional arguments for configuring the Title.")
    ] = {},
    scale_kws: Annotated[
        dict, Field(description="Additional arguments for configuring the Scale Bar.")
    ] = {},
    north_arrow_kws: Annotated[
        dict, Field(description="Additional arguments for configuring the North Arrow.")
    ] = {},
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
        m.add_title(title, **title_kws)

    m.add_scale_bar(**scale_kws)
    m.add_north_arrow(**north_arrow_kws)

    if tile_layer:
        m.add_layer(EcoMap.get_named_tile_layer(tile_layer))

    m.add_layer(geo_layers)
    m.zoom_to_bounds(m.layers)
    return m.to_html(title=title if title is not None else "Map Export")
