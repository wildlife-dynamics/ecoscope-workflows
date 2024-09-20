from typing import Annotated

from pydantic import Field
from ecoscope_workflows_core.annotations import AnyGeoDataFrame
from ecoscope_workflows_core.decorators import task


@task
def create_meshgrid(
    aoi: Annotated[
        AnyGeoDataFrame,
        Field(description="The area to create a meshgrid of.", exclude=True),
    ],
    cell_width: Annotated[
        int, Field(description="The width of a grid cell in meters.")
    ] = 5000,
    cell_height: Annotated[
        int, Field(description="The height of a grid cell in meters.")
    ] = 5000,
    intersecting_only: Annotated[
        bool,
        Field(
            description="Whether to return only grid cells intersecting with the aoi."
        ),
    ] = False,
) -> AnyGeoDataFrame:
    """
    Create a grid from the provided area of interest.
    """
    import geopandas as gpd  # type: ignore[import-untyped]
    from ecoscope.base.utils import create_meshgrid  # type: ignore[import-untyped]

    result = create_meshgrid(
        aoi.unary_union,
        in_crs=aoi.crs,
        out_crs=aoi.crs,
        xlen=cell_width,
        ylen=cell_height,
        return_intersecting_only=intersecting_only,
    )

    return gpd.GeoDataFrame(geometry=result)
