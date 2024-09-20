import logging
from typing import Annotated, cast

from pydantic import BaseModel, Field

from ecoscope_workflows_core.annotations import AnyGeoDataFrame
from ecoscope_workflows_core.decorators import task


logger = logging.getLogger(__name__)


class Coordinate(BaseModel):
    x: float
    y: float


@task
def apply_reloc_coord_filter(
    df: AnyGeoDataFrame,
    min_x: Annotated[float, Field(default=-180.0)] = -180.0,
    max_x: Annotated[float, Field(default=180.0)] = 180.0,
    min_y: Annotated[float, Field(default=-90.0)] = -90.0,
    max_y: Annotated[float, Field(default=90.0)] = 90.0,
    filter_point_coords: Annotated[
        list[Coordinate], Field(default=[Coordinate(x=0.0, y=0.0)])
    ] = [Coordinate(x=0.0, y=0.0)],
) -> AnyGeoDataFrame:
    import geopandas  # type: ignore[import-untyped]
    import shapely

    # TODO: move it to ecoscope core
    filter_point_coords = geopandas.GeoSeries(
        shapely.geometry.Point(coord.x, coord.y) for coord in filter_point_coords
    )

    def envelope_reloc_filter(geometry) -> bool:
        return (
            geometry.x > min_x
            and geometry.x < max_x
            and geometry.y > min_y
            and geometry.y < max_y
            and geometry not in filter_point_coords
        )

    return cast(
        AnyGeoDataFrame,
        df[df["geometry"].apply(envelope_reloc_filter)].reset_index(drop=True),
    )
