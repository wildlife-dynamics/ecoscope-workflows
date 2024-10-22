from importlib.resources import files

import geopandas as gpd  # type: ignore[import-untyped]
import pytest
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_time_density


def test_calculate_time_density():
    example_input_df_path = (
        files("ecoscope_workflows_ext_ecoscope.tasks.preprocessing")
        / "relocations-to-trajectory.example-return.parquet"
    )
    input_df = gpd.read_parquet(example_input_df_path)
    kws = dict(
        pixel_size=250.0,
        crs="ESRI:102022",
        band_count=1,
        nodata_value="nan",
        max_speed_factor=1.05,
        expansion_factor=1.3,
        percentiles=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0],
    )
    result = calculate_time_density(input_df, **kws)

    assert result.shape == (6, 3)
    assert all([column in result for column in ["percentile", "geometry", "area_sqkm"]])
    assert list(result["area_sqkm"]) == pytest.approx(
        [
            3223.8125,
            2468.6875,
            1622.8125,
            1121.875,
            785.6875,
            544.9375,
        ]
    )
