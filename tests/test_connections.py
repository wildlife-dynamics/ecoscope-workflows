import os
from unittest.mock import patch

import pytest
from pydantic import validate_call

from ecoscope_workflows.annotations import EarthRangerClient
from ecoscope_workflows.connections import EarthRangerConnection


def test_connection_no_prefix():
    mock_env = {
        "SERVER": "https://earthranger.com",
        "USERNAME": "user",
        "PASSWORD": "pass",
        "TCP_LIMIT": "5",
        "SUB_PAGE_SIZE": "4000",
    }
    with patch.dict(os.environ, mock_env):
        conn = EarthRangerConnection()
        assert conn.server == "https://earthranger.com"
        assert conn.username == "user"
        assert conn.password == "pass"
        assert conn.tcp_limit == 5
        assert conn.sub_page_size == 4000


@pytest.fixture
def named_mock_env():
    return {
        "MEP_DEV__SERVER": "https://mep-dev.pamdas.org",
        "MEP_DEV__USERNAME": "user",
        "MEP_DEV__PASSWORD": "pass",
        "MEP_DEV__TCP_LIMIT": "5",
        "MEP_DEV__SUB_PAGE_SIZE": "4000",
    }


def test_connection_with_named_prefix(named_mock_env):
    with patch.dict(os.environ, named_mock_env):
        conn = EarthRangerConnection.from_named_connection("MEP_DEV")
        assert conn.server == "https://mep-dev.pamdas.org"
        assert conn.username == "user"
        assert conn.password == "pass"
        assert conn.tcp_limit == 5
        assert conn.sub_page_size == 4000


def test_resolve_earthranger_client(named_mock_env):
    @validate_call(config={"arbitrary_types_allowed": True})
    def f(client: EarthRangerClient):
        return client

    with patch.dict(os.environ, named_mock_env):
        with patch("ecoscope.io.EarthRangerIO"):
            client = f(client="MEP_DEV")
            assert hasattr(client, "get_subjectgroup_observations")
            assert callable(client.get_subjectgroup_observations)


@pytest.mark.xfail
def test_google_secrets_manager(): ...
