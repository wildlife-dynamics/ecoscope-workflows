from pydantic import BaseModel


class LayerStyleProperty(BaseModel):
    auto_highlight: bool = False
    opacity: float = 1
    pickable: bool = True


class PathLayerProperty(LayerStyleProperty):
    get_color: list[int] = [0, 0, 0, 255]
    get_width: float = 1


class ShapeLayerProperty(LayerStyleProperty):
    filled: bool = True
    get_fill_color: list[int] = [0, 0, 0, 255]
    get_line_color: list[int] = [0, 0, 0, 255]
    get_line_width: float = 1


class ScatterPlotLayerProperty(ShapeLayerProperty):
    get_radius: float = 1


class PolygonLayerProperty(ShapeLayerProperty):
    extruded: bool = False
    get_elevation: float = 1000


class NorthArrowProperty(BaseModel):
    placement: str = "top-left"
