import logging
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrameSchema, DataFrame
from ecoscope_workflows.decorators import distributed

logger = logging.getLogger(__name__)


@distributed
def apply_reloc_filter(
    df: DataFrame[AnyGeoDataFrameSchema],
    filter_point_coords: Annotated[list[list[float]], Field()],
) -> DataFrame[AnyGeoDataFrameSchema]:
    from ecoscope.base import Relocations, RelocsCoordinateFilter

    relocs = Relocations(df)
    relocs.apply_reloc_filter(
        RelocsCoordinateFilter(filter_point_coords=filter_point_coords),
        inplace=True,
    )

    relocs.remove_filtered(inplace=True)
    return relocs
