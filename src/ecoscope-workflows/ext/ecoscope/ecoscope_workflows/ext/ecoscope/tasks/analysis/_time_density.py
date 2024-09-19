from typing import Annotated, Any

import pandera as pa
import pandera.typing as pa_typing
from pydantic import Field

from ecoscope_workflows.core.annotations import (
    AnyGeoDataFrame,
    DataFrame,
    JsonSerializableDataFrameModel,
)
from ecoscope_workflows.core.decorators import task


class TimeDensityReturnGDFSchema(JsonSerializableDataFrameModel):
    percentile: pa_typing.Series[float] = pa.Field()
    geometry: pa_typing.Series[Any] = pa.Field()  # see note above re: geometry typing
    area_sqkm: pa_typing.Series[float] = pa.Field()


@task
def calculate_time_density(
    trajectory_gdf: Annotated[
        AnyGeoDataFrame,
        Field(description="The trajectory geodataframe.", exclude=True),
    ],
    # raster profile
    pixel_size: Annotated[
        float,
        Field(default=250.0, description="Pixel size for raster profile."),
    ],
    crs: Annotated[str, Field(default="ESRI:102022")],
    nodata_value: Annotated[float, Field(default="nan", allow_inf_nan=True)],
    band_count: Annotated[int, Field(default=1)],
    # time density
    max_speed_factor: Annotated[float, Field(default=1.05)],
    expansion_factor: Annotated[float, Field(default=1.3)],
    percentiles: Annotated[
        list[float], Field(default=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0])
    ],
) -> DataFrame[TimeDensityReturnGDFSchema]:
    import tempfile

    from ecoscope.analysis.percentile import get_percentile_area  # type: ignore[import-untyped]
    from ecoscope.analysis.UD import calculate_etd_range  # type: ignore[import-untyped]
    from ecoscope.io.raster import RasterProfile  # type: ignore[import-untyped]

    raster_profile = RasterProfile(
        pixel_size=pixel_size,
        crs=crs,
        nodata_value=nodata_value,
        band_count=band_count,
    )
    trajectory_gdf.sort_values("segment_start", inplace=True)

    # FIXME: make `calculate_etd_range` return an in-memory raster which
    # we can pass to `get_percentile_area`, so we don't need the filesystem.
    tmp_tif_path = tempfile.NamedTemporaryFile(suffix=".tif")
    calculate_etd_range(
        trajectory_gdf=trajectory_gdf,
        output_path=tmp_tif_path,
        # Choose a value above the max recorded segment speed
        max_speed_kmhr=max_speed_factor * trajectory_gdf["speed_kmhr"].max(),
        raster_profile=raster_profile,
        expansion_factor=expansion_factor,
    )
    result = get_percentile_area(
        percentile_levels=percentiles,
        raster_path=tmp_tif_path,
    )
    result.drop(columns="subject_id", inplace=True)
    result["area_sqkm"] = result.area / 1000000.0
    return result
