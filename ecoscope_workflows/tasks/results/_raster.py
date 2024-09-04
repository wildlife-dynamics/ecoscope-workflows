from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import Field

from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


@dataclass
class RasterObject:
    image: Any


@task
def grid_to_raster(
    geodataframe: Annotated[
        AnyGeoDataFrame,
        Field(description="The data to rasterize.", exclude=True),
    ],
    value_column: Annotated[
        str, Field(description="The dataframe column with values to rasterize.")
    ] = "",
) -> RasterObject:
    """
    Save a GeoDataFrame grid to a raster.

    Args:
        geodataframe (gpd.GeoDataFrame): The input geodataframe.
        val_column (str): The dataframe column with values to rasterize..
        cell_width (int): The width of the raster cells in meters.
        cell_height (int): The height of the raster cells in meters.

    Returns:
        The generated RasterObject
    """
    from ecoscope.io.raster import grid_to_raster

    return RasterObject(
        image=grid_to_raster(
            grid=geodataframe,
            val_column=value_column,
        )
    )
