from typing import Annotated, Protocol

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import distributed


class EcoMapProtocol(Protocol):
    """Protocol for EcoMap objects, to avoid importing mapping dependencies
    at the top level of the module.
    """

    def to_html(self): ...


@distributed
def draw_ecomap(
    geodataframe: AnyGeoDataFrame,
    static: Annotated[bool, Field()],
    height: Annotated[int, Field()],
    width: Annotated[int, Field()],
    search_control: Annotated[bool, Field()],
    title: Annotated[str, Field()],
    title_kws: Annotated[dict, Field(default_factory=dict)],
    tile_layers: Annotated[list[dict], Field()],
    north_arrow_kws: Annotated[dict, Field(default_factory=dict)],
    add_gdf_kws: Annotated[dict, Field(default_factory=dict)],
) -> Annotated[EcoMapProtocol, Field()]:
    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, height=height, width=width, search_control=search_control)
    m.add_title(title=title, **title_kws)

    for tl in tile_layers:
        m.add_tile_layer(**tl)

    m.add_north_arrow(**north_arrow_kws)
    m.add_gdf(geodataframe, **add_gdf_kws)
    m.zoom_to_gdf(geodataframe)

    return m
