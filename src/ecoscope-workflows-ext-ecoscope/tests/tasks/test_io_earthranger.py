import os
from datetime import datetime, timezone

import pytest
from ecoscope_workflows_core.tasks.filter._filter import TimeRange
from ecoscope_workflows_ext_ecoscope.connections import EarthRangerConnection
from ecoscope_workflows_ext_ecoscope.tasks.io import (
    get_events,
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
        subject_group_name="Ecoscope",
        include_inactive=True,
        time_range=TimeRange(
            since=datetime.strptime("2017-01-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
            until=datetime.strptime("2017-03-31", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
        ),
    )

    assert len(result) > 0
    assert "geometry" in result
    assert "groupby_col" in result
    assert "fixtime" in result
    assert "junk_status" in result


def test_get_patrol_observations(client):
    result = get_patrol_observations(
        client=client,
        time_range=TimeRange(
            since=datetime.strptime("2015-01-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
            until=datetime.strptime("2015-03-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
        ),
        patrol_type="05ad114e-1aff-4602-bc83-efd333cdd8a2",
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
        time_range=TimeRange(
            since=datetime.strptime("2015-01-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
            until=datetime.strptime("2015-03-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
        ),
        patrol_type="05ad114e-1aff-4602-bc83-efd333cdd8a2",
        status=None,
    )

    assert len(result) > 0
    assert "id" in result
    assert "event_type" in result
    assert "geometry" in result


def test_get_events(client):
    result = get_events(
        client=client,
        time_range=TimeRange(
            since=datetime.strptime("2015-01-01", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
            until=datetime.strptime("2015-12-31", "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            ),
        ),
        event_types=[
            "hwc_rep",
            "bird_sighting_rep",
            "wildlife_sighting_rep",
            "poacher_camp_rep",
            "fire_rep",
            "injured_animal_rep",
        ],
        event_columns=["id", "time", "event_type", "geometry"],
    )

    assert len(result) > 0
    assert "id" in result
    assert "time" in result
    assert "event_type" in result
    assert "geometry" in result


def test_bad_token_fails():
    with pytest.raises(Exception, match="Authorization token is invalid or expired."):
        EarthRangerConnection(
            server=os.environ["EARTHRANGER_SERVER"],
            token="abc123",
            tcp_limit="5",
            sub_page_size="4000",
        ).get_client()
