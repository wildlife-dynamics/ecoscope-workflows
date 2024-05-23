from importlib import resources
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest

from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.python.preprocessing import (
    process_relocations,
    relocations_to_trajectory,
)


@pytest.fixture
def observations_parquet_path():
    return (
        resources.files("ecoscope_workflows.tasks.python.io")
        / "get-subjectgroup-observations.parquet"
    )


def test_process_relocations(observations_parquet_path: str, tmp_path):
    observations = gpd.read_parquet(observations_parquet_path)
    kws = dict(
        filter_point_coords=[[180, 90], [0, 0]],
        relocs_columns=["groupby_col", "fixtime", "junk_status", "geometry"],
    )
    in_memory = process_relocations(observations, **kws)

    # compare to `distributed` calling style
    def serialize_result(gdf: gpd.GeoDataFrame) -> str:
        path: Path = tmp_path / "result.parquet"
        gdf.to_parquet(path)
        return path.as_posix()

    result_path = process_relocations.replace(
        arg_prevalidators={"observations": gpd_from_parquet_uri},
        return_postvalidator=serialize_result,
        validate=True,
    )(observations_parquet_path, **kws)
    distributed_result = gpd.read_parquet(result_path)

    pd.testing.assert_frame_equal(in_memory, distributed_result)

    # we've cached this result for downstream tests, to make sure the cache is not stale
    cached = gpd.read_parquet(
        resources.files("ecoscope_workflows.tasks.python.preprocessing")
        / "process-relocations.parquet"
    )
    pd.testing.assert_frame_equal(in_memory, cached)


@pytest.fixture
def process_relocations_parquet_path():
    return (
        resources.files("ecoscope_workflows.tasks.python.preprocessing")
        / "process-relocations.parquet"
    )


def test_relocations_to_trajectory(process_relocations_parquet_path: str, tmp_path):
    relocations = gpd.read_parquet(process_relocations_parquet_path)
    kws = dict(
        min_length_meters=0.001,
        max_length_meters=10000,
        min_time_secs=1,
        max_time_secs=3600,
        min_speed_kmhr=0.0,
        max_speed_kmhr=120,
    )
    in_memory = relocations_to_trajectory(relocations, **kws)

    # compare to `distributed` calling style
    def serialize_result(gdf: gpd.GeoDataFrame) -> str:
        path: Path = tmp_path / "result.parquet"
        gdf.to_parquet(path)
        return path.as_posix()

    result_path = relocations_to_trajectory.replace(
        arg_prevalidators={"relocations": gpd_from_parquet_uri},
        return_postvalidator=serialize_result,
        validate=True,
    )(process_relocations_parquet_path, **kws)
    distributed_result = gpd.read_parquet(result_path)

    pd.testing.assert_frame_equal(in_memory, distributed_result)

    # we've cached this result for downstream tests, to make sure the cache is not stale
    cached = gpd.read_parquet(
        resources.files("ecoscope_workflows.tasks.python.preprocessing")
        / "relocations-to-trajectory.parquet"
    )
    pd.testing.assert_frame_equal(in_memory, cached)
