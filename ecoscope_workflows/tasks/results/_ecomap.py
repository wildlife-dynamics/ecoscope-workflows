from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import distributed


@distributed
def draw_ecomap(
    geodataframe: AnyGeoDataFrame,
    static: Annotated[bool, Field()],
    height: Annotated[int, Field()],
    width: Annotated[int, Field()],
    search_control: Annotated[bool, Field()],
    title: Annotated[str, Field()],
    title_kws: Annotated[dict, Field()],
    tile_layers: Annotated[list[dict], Field()],
    north_arrow_kws: Annotated[dict, Field()],
    add_gdf_kws: Annotated[dict, Field()],
) -> Annotated[str, Field()]:
    print("Importing EcoMap")
    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, height=height, width=width, search_control=search_control)
    m.add_title(title=title, **title_kws)
    print("Adding tile layers")
    for tl in tile_layers:
        m.add_tile_layer(**tl)

    m.add_north_arrow(**north_arrow_kws)
    print("Adding GeoDataFrame")
    m.add_gdf(geodataframe, **add_gdf_kws)
    print("Zooming to GeoDataFrame")
    m.zoom_to_gdf(geodataframe)
    print("Rendering html")
    return m._repr_html_(fill_parent=True)
