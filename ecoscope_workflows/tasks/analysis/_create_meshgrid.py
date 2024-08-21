from typing import Annotated

import pandera as pa
from pydantic import Field
from pydantic.json_schema import SkipJsonSchema
from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


@task
def create_meshgrid(
    aoi: Annotated[
        AnyGeoDataFrame,
        Field(description="The area to create a meshgrid of.", exclude=True),
    ],
    cell_width: Annotated[
        int, Field(description="The width of a grid cell in meters.")
    ] = 5000,
    cell_hieght: Annotated[
        int, Field(description="The height of a grid cell in meters.")
    ] = 5000,
    intersecting_only: Annotated[
        bool, Field(description="The height of a grid cell in meters.")
    ] = True,
    existing_grid: Annotated[
        AnyGeoDataFrame | pa.typing.geopandas.GeoSeries | SkipJsonSchema[None],
        Field(
            description="If provided, attempts to align created grid to start of existing grid. Requires a CRS and valid geometry."
        ),
    ] = None,
) -> pa.typing.geopandas.GeoSeries:
    """
    Create a grid from the provided area of interest.
    """
    from ecoscope.base.utils import create_meshgrid

    result = create_meshgrid(
        aoi.unary_union,
        in_crs=aoi.crs,
        out_crs=aoi.crs,
        xlen=cell_width,
        ylen=cell_hieght,
        return_intersecting_only=intersecting_only,
        align_to_existing=existing_grid,
    )

    return result
