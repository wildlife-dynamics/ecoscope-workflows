from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.tasks.results._map_config import (
    LayerStyleProperty,
    NorthArrowProperty,
)


@distributed
def draw_ecomap(
    geodataframe: Annotated[
        AnyGeoDataFrame, Field(description="The geodataframe to visualize.")
    ],
    data_type: Annotated[
        Literal["Scatterplot", "Path", "Polygon"],
        Field(description="The type of visualization."),
    ],
    # TODO: react-jsonschema-form: select different layer props based on the input of data_type
    style_props: Annotated[
        LayerStyleProperty,
        Field(description="Style arguments for the data visualization."),
    ] = LayerStyleProperty(),
    tile_layer: Annotated[
        str, Field(description="A named tile layer, ie OpenStreetMap.")
    ] = "",
    static: Annotated[
        bool, Field(description="Set to true to disable map pan/zoom.")
    ] = False,
    title: Annotated[str, Field(description="The map title.")] = "",
    north_arrow_props: Annotated[
        NorthArrowProperty,
        Field(description="Additional arguments for configuring the North Arrow."),
    ] = NorthArrowProperty(),
) -> Annotated[str, Field()]:
    """
    Creates a map based on the provided layer definitions and configuration.

    Args:
    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.
    data_type (str): The type of visualization, "Scatterplot", "Path" or "Polygon".
    style_props (LayerStyleProperty): Style arguments for the data visualization.
    tile_layer (str): A named tile layer, ie OpenStreetMap.
    static (bool): Set to true to disable map pan/zoom.
    title (str): The map title.
    north_arrow_props (NorthArrowProperty): Additional arguments for configuring the North Arrow.

    Returns:
    str: A static HTML representation of the map.
    """

    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, default_widgets=False)

    if title:
        m.add_title(title)

    m.add_scale_bar()
    m.add_north_arrow(**north_arrow_props.model_dump())

    if tile_layer:
        m.add_layer(EcoMap.get_named_tile_layer(tile_layer))

    match data_type:
        case "Scatterplot":
            m.add_scatterplot_layer(geodataframe, **style_props.model_dump())
        case "Path":
            m.add_path_layer(geodataframe, **style_props.model_dump())
        case "Polygon":
            m.add_polygon_layer(geodataframe, **style_props.model_dump())

    m.zoom_to_bounds(m.layers)
    return m.to_html()
