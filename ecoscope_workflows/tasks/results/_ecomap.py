from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


@task
def draw_ecomap(
    geodataframe: Annotated[
        AnyGeoDataFrame, Field(description="The geodataframe to visualize.")
    ],
    data_type: Annotated[
        Literal["Scatterplot", "Path", "Polygon"],
        Field(description="The type of visualization."),
    ],
    style_kws: Annotated[
        dict, Field(description="Style arguments for the data visualization.")
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

    match data_type:
        case "Scatterplot":
            m.add_scatterplot_layer(geodataframe, **style_kws)
        case "Path":
            m.add_path_layer(geodataframe, **style_kws)
        case "Polygon":
            m.add_polygon_layer(geodataframe, **style_kws)

    m.zoom_to_bounds(m.layers)
    return m.to_html()
