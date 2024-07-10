from datetime import datetime
from importlib.resources import files

import os
import geopandas as gpd
import pandas as pd
import pytest

from ecoscope_workflows.connections import EarthRangerConnection
from ecoscope_workflows.tasks.io import get_subjectgroup_observations

pytestmark = pytest.mark.io


def test_get_subject_group_observations():
    result = get_subjectgroup_observations(
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
    )

    cached = gpd.read_parquet(
        str(
            files("ecoscope_workflows.tasks.io")
            / "get-subjectgroup-observations.example-return.parquet"
        )
    )

    pd.testing.assert_frame_equal(result, cached)
