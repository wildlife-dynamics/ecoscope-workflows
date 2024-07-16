import os
from datetime import datetime
from importlib.resources import files

import geopandas as gpd
import pandas as pd
import pytest

from ecoscope_workflows.connections import EarthRangerConnection
from ecoscope_workflows.tasks.io import (
    get_patrol_observations,
    get_subjectgroup_observations,
)

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
            / "get-subjectgroup-observations.example-return.updated.parquet"
        )
    )

    pd.testing.assert_frame_equal(result, cached)


def test_get_patrol_observations():
    result = get_patrol_observations(
        client=EarthRangerConnection(
            server=os.environ["EARTHRANGER_SERVER"],
            username=os.environ["EARTHRANGER_USERNAME"],
            password=os.environ["EARTHRANGER_PASSWORD"],
            tcp_limit="5",
            sub_page_size="4000",
        ).get_client(),
        since="2011-01-01",
        until="2023-01-01",
        # MEP_Distance_Survey_Patrol
        patrol_type="0ef3bf48-b44c-4a4e-a145-7ab2e38c9a57",
        status=None,
        include_patrol_details=True,
    )

    cached = gpd.read_parquet(
        str(
            files("ecoscope_workflows.tasks.io")
            / "get-patrol-observations.example-return.parquet"
        )
    )

    pd.testing.assert_frame_equal(result, cached)
