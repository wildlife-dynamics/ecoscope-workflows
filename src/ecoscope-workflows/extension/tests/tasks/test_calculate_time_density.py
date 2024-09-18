from importlib.resources import files

import geopandas as gpd  # type: ignore[import-untyped]

from ecoscope_workflows.extension.tasks.analysis import calculate_time_density


def test_calculate_time_density():
    example_input_df_path = (
        files("ecoscope_workflows.extension.tasks.preprocessing")
        / "relocations-to-trajectory.example-return.parquet"
    )
    input_df = gpd.read_parquet(example_input_df_path)
    kws = dict(
        pixel_size=250.0,
        crs="ESRI:102022",
        band_count=1,
        nodata_value=float("nan"),
        max_speed_factor=1.05,
        expansion_factor=1.3,
        percentiles=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0],
    )
    result = calculate_time_density(input_df, **kws)

    assert result.shape == (6, 3)
    assert all([column in result for column in ["percentile", "geometry", "area_sqkm"]])
    assert list(result["area_sqkm"]) == [17.75, 13.4375, 8.875, 6.25, 4.4375, 3.125]
