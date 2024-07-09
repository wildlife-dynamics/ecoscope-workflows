from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import distributed


@dataclass
class LayerDefinition:
    data: AnyGeoDataFrame
    layer_type: Literal["Scatterplot", "Path", "Polygon"]
    style_kws: dict


@distributed
def draw_ecomap(
    layers: Annotated[list[LayerDefinition] | LayerDefinition, Field()],
    tile_layer: Annotated[str | None, Field()] = None,
    static: Annotated[bool, Field()] = False,
    title: Annotated[str | None, Field()] = None,
    title_kws: Annotated[dict, Field()] = {},
    scale_kws: Annotated[dict, Field()] = {},
    north_arrow_kws: Annotated[dict, Field()] = {},
) -> Annotated[str, Field()]:
    from ecoscope.mapping import EcoMap

    m = EcoMap(static=static, default_widgets=False)

    if title:
        m.add_title(title, **title_kws)

    m.add_scale_bar(**scale_kws)
    m.add_north_arrow(**north_arrow_kws)

    if tile_layer is not None:
        m.add_layer(EcoMap.get_named_tile_layer(tile_layer))

    if isinstance(layers, LayerDefinition):
        layers = [layers]
    for layer in layers:
        match layer.layer_type:
            case "Scatterplot":
                m.add_scatterplot_layer(layer.data, **layer.style_kws)
            case "Path":
                m.add_path_layer(layer.data, **layer.style_kws)
            case "Polygon":
                m.add_polygon_layer(layer.data, **layer.style_kws)

    m.zoom_to_bounds(m.layers)
    return m.to_html()
