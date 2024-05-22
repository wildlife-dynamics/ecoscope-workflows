from pathlib import Path

import pandas as pd
import pytest
import geopandas as gpd

from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.python.analysis import calculate_time_density


@pytest.fixture
def trajectory_parquet_path() -> str:
    return (Path(__file__).parent.parent / "data" / "trajectory.parquet").as_posix()


@pytest.fixture
def trajectory_gdf(trajectory_parquet_path: str) -> gpd.GeoDataFrame:
    return gpd.read_parquet(trajectory_parquet_path)


def test_calculate_time_density(
    trajectory_parquet_path: str,
    trajectory_gdf: gpd.GeoDataFrame,
    tmp_path,
):
    raster_kws = dict(
        pixel_size=250.0,
        crs="ESRI:102022",
        band_count=1,
        nodata_value=float("nan"),
    )
    density_kws = dict(
        max_speed_factor=1.05,
        expansion_factor=1.3,
        percentiles=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0],
    )
    kws = raster_kws | density_kws
    in_memory = calculate_time_density(trajectory_gdf, **kws)
    assert in_memory.shape == (6, 3)
    assert all(
        [column in in_memory for column in ["percentile", "geometry", "area_sqkm"]]
    )
    assert list(in_memory["area_sqkm"]) == [17.75, 13.4375, 8.875, 6.25, 4.4375, 3.125]

    # compare to `distributed` calling style
    def serialize_result(gdf: gpd.GeoDataFrame) -> str:
        path: Path = tmp_path / "result.parquet"
        gdf.to_parquet(path)
        return path.as_posix()

    # note two things: we are passing *a path*, not a GeoDataFrame, and we also return a path
    result_path = calculate_time_density.replace(
        arg_prevalidators={"trajectory_gdf": gpd_from_parquet_uri},
        return_postvalidator=serialize_result,
        validate=True,
    )(trajectory_parquet_path, **kws)
    # the result of this call *is a path* to the serialized result, so we need to load it from disk
    distributed_result = gpd.read_parquet(result_path)
    # assert distributed result is the same as the in_memory result
    pd.testing.assert_frame_equal(in_memory, distributed_result)
