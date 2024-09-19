import os
from datetime import datetime

import pytest

from ecoscope_workflows.ext.ecoscope.connections import EarthRangerConnection
from ecoscope_workflows.ext.ecoscope.tasks.io import (
    get_patrol_events,
    get_patrol_observations,
    get_subjectgroup_observations,
)

pytestmark = pytest.mark.io


@pytest.fixture
def client():
    return EarthRangerConnection(
        server=os.environ["EARTHRANGER_SERVER"],
        username=os.environ["EARTHRANGER_USERNAME"],
        password=os.environ["EARTHRANGER_PASSWORD"],
        tcp_limit="5",
        sub_page_size="4000",
    ).get_client()


def test_get_subject_group_observations(client):
    result = get_subjectgroup_observations(
        client=client,
        subject_group_name="Elephants",
        include_inactive=True,
        since=datetime.strptime("2011-01-01", "%Y-%m-%d"),
        until=datetime.strptime("2023-01-01", "%Y-%m-%d"),
    )

    assert len(result) > 0
    assert "geometry" in result
    assert "groupby_col" in result
    assert "fixtime" in result
    assert "junk_status" in result


def test_get_patrol_observations(client):
    result = get_patrol_observations(
        client=client,
        since="2011-01-01",
        until="2023-01-01",
        # MEP_Distance_Survey_Patrol
        patrol_type="0ef3bf48-b44c-4a4e-a145-7ab2e38c9a57",
        status=None,
        include_patrol_details=True,
    )

    assert len(result) > 0
    assert "geometry" in result
    assert "groupby_col" in result
    assert "fixtime" in result
    assert "junk_status" in result


def test_get_patrol_events(client):
    result = get_patrol_events(
        client=client,
        since="2011-01-01",
        until="2025-01-01",
        patrol_type=None,
        status=None,
    )

    assert len(result) > 0
    assert "id" in result
    assert "event_type" in result
    assert "geometry" in result
