import logging
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrameSchema, DataFrame
from ecoscope_workflows.decorators import distributed

logger = logging.getLogger(__name__)


@distributed
def apply_reloc_filter_envelope(
    df: DataFrame[AnyGeoDataFrameSchema],
    min_x: Annotated[float, Field(default=-180.0)] = -180.0,
    max_x: Annotated[float, Field(default=180.0)] = 180.0,
    min_y: Annotated[float, Field(default=-90.0)] = -90.0,
    max_y: Annotated[float, Field(default=90.0)] = 90.0,
    filter_point_coords: Annotated[list[list[float]], Field(default=[[0.0, 0.0]])] = [
        [0.0, 0.0]
    ],
) -> DataFrame[AnyGeoDataFrameSchema]:
    # TODO: move it to ecoscope core
    def apply_reloc_filter(geometry) -> DataFrame[AnyGeoDataFrameSchema]:
        return (
            geometry.x > min_x
            and geometry.x < max_x
            and geometry.y > min_y
            and geometry.y < max_y
            and geometry not in filter_point_coords
        )

    return df[df["geometry"].apply(apply_reloc_filter)]
