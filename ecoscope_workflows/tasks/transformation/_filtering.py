import logging
from typing import Annotated, TYPE_CHECKING, cast

from pydantic import BaseModel, Field

from ecoscope_workflows.annotations import AnyGeoDataFrameSchema, DataFrame
from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


class Coordinate(BaseModel):
    x: float
    y: float


@task
def apply_reloc_coord_filter(
    df: DataFrame[AnyGeoDataFrameSchema],
    min_x: Annotated[float, Field(default=-180.0)] = -180.0,
    max_x: Annotated[float, Field(default=180.0)] = 180.0,
    min_y: Annotated[float, Field(default=-90.0)] = -90.0,
    max_y: Annotated[float, Field(default=90.0)] = 90.0,
    filter_point_coords: Annotated[
        list[Coordinate], Field(default=[Coordinate(x=0.0, y=0.0)])
    ] = [Coordinate(x=0.0, y=0.0)],
) -> DataFrame[AnyGeoDataFrameSchema]:
    import geopandas  # type: ignore[import-untyped]
    import shapely

    if TYPE_CHECKING:
        import pandas as pd

        cast(pd.DataFrame, df)

    # TODO: move it to ecoscope core
    filter_point_coords = geopandas.GeoSeries(
        shapely.geometry.Point(coord.x, coord.y) for coord in filter_point_coords
    )

    def envelope_reloc_filter(geometry) -> DataFrame[AnyGeoDataFrameSchema]:
        return (
            geometry.x > min_x
            and geometry.x < max_x
            and geometry.y > min_y
            and geometry.y < max_y
            and geometry not in filter_point_coords
        )

    return df[df["geometry"].apply(envelope_reloc_filter)].reset_index(drop=True)
