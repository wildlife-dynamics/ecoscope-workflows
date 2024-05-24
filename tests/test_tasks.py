from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Callable

import geopandas as gpd
import pandas as pd
import pytest

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.preprocessing import (
    process_relocations,
    relocations_to_trajectory,
)


@dataclass
class TaskFixture:
    task: distributed
    input_dataframe_arg_name: str
    example_input_dataframe_path: str
    kws: dict
    assert_that_return_dataframe: list[Callable[[gpd.GeoDataFrame], bool]]
    example_return_path: str


task_fixtures = {
    "process_relocations": TaskFixture(
        task=process_relocations,
        input_dataframe_arg_name="observations",
        example_input_dataframe_path=str(
            files("ecoscope_workflows.tasks.io")
            / "get-subjectgroup-observations.example-return.parquet"
        ),
        kws=dict(
            filter_point_coords=[[180, 90], [0, 0]],
            relocs_columns=["groupby_col", "fixtime", "junk_status", "geometry"],
        ),
        assert_that_return_dataframe=[
            lambda df: hasattr(df, "geometry"),  # smoke test
        ],
        example_return_path=str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "process-relocations.example-return.parquet"
        ),
    ),
    "relocations_to_trajectory": TaskFixture(
        task=relocations_to_trajectory,
        input_dataframe_arg_name="relocations",
        example_input_dataframe_path=str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "process-relocations.example-return.parquet"
        ),
        kws=dict(
            min_length_meters=0.001,
            max_length_meters=10000,
            min_time_secs=1,
            max_time_secs=3600,
            min_speed_kmhr=0.0,
            max_speed_kmhr=120,
        ),
        assert_that_return_dataframe=[
            lambda df: hasattr(df, "geometry"),  # smoke test
        ],
        example_return_path=str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "relocations-to-trajectory.example-return.parquet"
        ),
    ),
    "calculate_time_density": TaskFixture(
        task=calculate_time_density,
        input_dataframe_arg_name="trajectory_gdf",
        example_input_dataframe_path=str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "relocations-to-trajectory.example-return.parquet"
        ),
        kws=dict(
            pixel_size=250.0,
            crs="ESRI:102022",
            band_count=1,
            nodata_value=float("nan"),
            max_speed_factor=1.05,
            expansion_factor=1.3,
            percentiles=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0],
        ),
        assert_that_return_dataframe=[
            lambda df: df.shape == (6, 3),
            lambda df: all(
                [column in df for column in ["percentile", "geometry", "area_sqkm"]]
            ),
            lambda df: list(df["area_sqkm"])
            == [17.75, 13.4375, 8.875, 6.25, 4.4375, 3.125],
        ],
        example_return_path=str(
            files("ecoscope_workflows.tasks.analysis")
            / "calculate-time-density.example-return.parquet"
        ),
    ),
}


@pytest.mark.parametrize(
    "tf",
    task_fixtures.values(),
    ids=task_fixtures.keys(),
)
def test_consumes_and_produces_dataframe(
    tf: TaskFixture,
    tmp_path: Path,
):
    input_dataframe = gpd.read_parquet(tf.example_input_dataframe_path)
    in_memory = tf.task(input_dataframe, **tf.kws)

    for assert_fn in tf.assert_that_return_dataframe:
        assert assert_fn(in_memory)

    # we've cached this result for reuse by other tests, so check that cache is not stale
    cached = gpd.read_parquet(tf.example_return_path)
    pd.testing.assert_frame_equal(in_memory, cached)

    # compare to `distributed` calling style
    def serialize_result(gdf: gpd.GeoDataFrame) -> str:
        path: Path = tmp_path / "result.parquet"
        gdf.to_parquet(path)
        return path.as_posix()

    result_path = tf.task.replace(
        arg_prevalidators={tf.input_dataframe_arg_name: gpd_from_parquet_uri},
        return_postvalidator=serialize_result,
        validate=True,
    )(tf.example_input_dataframe_path, **tf.kws)
    # this time, the result is written to a file, so we need to read it back in
    distributed_result = gpd.read_parquet(result_path)
    # and ensure it's the same as the in-memory result
    pd.testing.assert_frame_equal(in_memory, distributed_result)
