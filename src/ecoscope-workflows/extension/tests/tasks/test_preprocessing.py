from importlib.resources import files

import geopandas as gpd  # type: ignore[import-untyped]
import pandas as pd

from ecoscope_workflows.extension.tasks.preprocessing import (
    process_relocations,
    relocations_to_trajectory,
)
from ecoscope_workflows.extension.tasks.transformation._filtering import Coordinate


def test_process_relocations():
    example_input_df_path = (
        files("ecoscope_workflows.extension.tasks.io")
        / "get-subjectgroup-observations.example-return.parquet"
    )
    input_df = gpd.read_parquet(example_input_df_path)
    kws = dict(
        filter_point_coords=[Coordinate(x=180, y=90), Coordinate(x=0, y=0)],
        relocs_columns=["groupby_col", "fixtime", "junk_status", "geometry"],
    )
    result = process_relocations(input_df, **kws)

    assert hasattr(result, "geometry")

    # we've cached this result for reuse by other tests, so check that cache is not stale
    cached_result_path = (
        files("ecoscope_workflows.extension.tasks.preprocessing")
        / "process-relocations.example-return.parquet"
    )
    cached = gpd.read_parquet(cached_result_path)
    pd.testing.assert_frame_equal(result, cached)


def test_relocations_to_trajectory():
    example_input_df_path = (
        files("ecoscope_workflows.extension.tasks.preprocessing")
        / "process-relocations.example-return.parquet"
    )
    input_df = gpd.read_parquet(example_input_df_path)
    kws = dict(
        min_length_meters=0.001,
        max_length_meters=10000,
        min_time_secs=1,
        max_time_secs=3600,
        min_speed_kmhr=0.0,
        max_speed_kmhr=120,
    )
    result = relocations_to_trajectory(input_df, **kws)

    assert hasattr(result, "geometry")

    # we've cached this result for reuse by other tests, so check that cache is not stale
    cached_result_path = (
        files("ecoscope_workflows.extension.tasks.preprocessing")
        / "relocations-to-trajectory.example-return.parquet"
    )
    cached = gpd.read_parquet(cached_result_path)
    pd.testing.assert_frame_equal(result, cached)
