from dataclasses import dataclass
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Callable

import os
import geopandas as gpd
import pandas as pd
import pytest


from ecoscope_workflows.connections import EarthRangerConnection
from ecoscope_workflows.decorators import DistributedTask
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.serde import gpd_from_parquet_uri

pytestmark = pytest.mark.io


@dataclass
class TaskFixture:
    task: DistributedTask
    input_dataframe_arg_name: str
    example_input_dataframe_path: str
    kws: dict
    assert_that_return_dataframe: list[Callable[[gpd.GeoDataFrame], bool]]
    example_return_path: str


task_fixtures = {
    "get_subjectgroup_observations": pytest.param(
        TaskFixture(
            task=get_subjectgroup_observations,
            input_dataframe_arg_name="",
            example_input_dataframe_path="",
            kws=dict(
                client=EarthRangerConnection(
                    server=os.environ["EARTHRANGER_SERVER"],
                    username=os.environ["EARTHRANGER_USERNAME"],
                    password=os.environ["EARTHRANGER_PASSWORD"],
                    tcp_limit="5",
                    sub_page_size="4000",
                ).get_client(),
                subject_group_name="Elephants",
                include_inactive=True,
                since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
                until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
            ),
            assert_that_return_dataframe=[
                lambda df: all(
                    [
                        col in df
                        for col in ["geometry", "groupby_col", "fixtime", "junk_status"]
                    ]
                ),
            ],
            example_return_path=str(
                files("ecoscope_workflows.tasks.io")
                / "get-subjectgroup-observations.example-return.parquet"
            ),
        )
    )
}


@pytest.mark.parametrize(
    "tf",
    task_fixtures.values(),
    ids=task_fixtures.keys(),
)
def test_consumes_and_or_produces_dataframe(
    tf: TaskFixture,
    tmp_path: Path,
):
    args = (
        (gpd.read_parquet(tf.example_input_dataframe_path),)
        if tf.example_input_dataframe_path
        else ()  # io tasks don't have input dataframes
    )
    in_memory = tf.task(*args, **tf.kws)

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
        arg_prevalidators=(
            {tf.input_dataframe_arg_name: gpd_from_parquet_uri}
            if tf.input_dataframe_arg_name
            else {}  # io tasks don't have input dataframes
        ),
        return_postvalidator=serialize_result,
        validate=True,
    )(tf.example_input_dataframe_path, **tf.kws)
    # this time, the result is written to a file, so we need to read it back in
    distributed_result = gpd.read_parquet(result_path)
    # and ensure it's the same as the in-memory result
    pd.testing.assert_frame_equal(in_memory, distributed_result)
