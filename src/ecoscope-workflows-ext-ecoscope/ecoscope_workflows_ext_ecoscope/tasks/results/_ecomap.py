from dataclasses import dataclass
from typing import Annotated, Literal, Union

from ecoscope_workflows_core.annotations import AnyGeoDataFrame
from ecoscope_workflows_core.decorators import task
from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

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
    get_width: float = 3
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
    get_radius: float = 5
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
    label_column: str | SkipJsonSchema[None] = None
    color_column: str | SkipJsonSchema[None] = None
    labels: list[str] | SkipJsonSchema[None] = None
    colors: list[str] | SkipJsonSchema[None] = None


@dataclass
class LayerDefinition:
    geodataframe: AnyGeoDataFrame
    layer_style: LayerStyle
    legend: LegendDefinition


@dataclass
class TileLayer:
    name: str
    opacity: float = 1


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
    tile_layers: Annotated[
        list[TileLayer],
        Field(description="A list of named tile layer with opacity, ie OpenStreetMap."),
    ] = [],
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
    tile_layers (list): A named tile layer, ie OpenStreetMap.
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
    m.add_save_image()

    for tile_layer in tile_layers:
        layer = EcoMap.get_named_tile_layer(tile_layer.name)
        layer.opacity = tile_layer.opacity
        m.add_layer(layer)

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
            if layer_def.legend.label_column and layer_def.legend.color_column:
                legend_labels.extend(
                    layer_def.geodataframe[layer_def.legend.label_column]
                )
                legend_colors.extend(
                    layer_def.geodataframe[layer_def.legend.color_column].apply(
                        color_to_hex
                    )
                )
            elif layer_def.legend.labels and layer_def.legend.colors:
                legend_labels.extend(layer_def.legend.labels)
                legend_colors.extend(layer_def.legend.colors)

        m.add_layer(layer)

    if len(legend_labels) > 0:
        m.add_legend(
            labels=[str(ll) for ll in legend_labels],
            colors=legend_colors,
            **(legend_style.model_dump(exclude_none=True)),  # type: ignore[union-attr]
        )

    m.zoom_to_bounds(m.layers)
    return m.to_html()


def color_to_hex(color):
    if isinstance(color, str) and color.startswith("#"):
        return color  # Already in hex format
    elif isinstance(color, (tuple, list)) and len(color) in (3, 4):
        if len(color) == 3:
            r, g, b = color
            a = 255
        else:
            r, g, b, a = color

        # Ensure all values are in 0-255 range
        r, g, b = (
            int(r * 255 if r <= 1 else r),
            int(g * 255 if g <= 1 else g),
            int(b * 255 if b <= 1 else b),
        )
        a = int(a * 255 if a <= 1 else a)

        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    else:
        return str(color)  # Return as string if it's neither hex nor valid tuple
