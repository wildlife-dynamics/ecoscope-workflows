import os
from unittest.mock import patch

from ecoscope_workflows.connections import EarthRangerConnection


def test_earthranger_connection():
    mock_env = {
        "SERVER": "https://earthranger.com",
        "USERNAME": "user",
        "PASSWORD": "pass",
        "TCP_LIMIT": "5",
        "SUB_PAGE_SIZE": "4000",
    }
    with patch.dict(os.environ, mock_env):
        er = EarthRangerConnection()
        assert er.server == "https://earthranger.com"
        assert er.username == "user"
        assert er.password == "pass"
        assert er.tcp_limit == 5
        assert er.sub_page_size == 4000


def test_named_earthranger_connection():
    mock_env = {
        "ER_SERVER": "https://earthranger.com",
        "ER_USERNAME": "user",
        "ER_PASSWORD": "pass",
        "ER_TCP_LIMIT": "5",
        "ER_SUB_PAGE_SIZE": "4000",
    }
    with patch.dict(os.environ, mock_env):
        er = EarthRangerConnection.from_named_connection("ER")
        assert er.server == "https://earthranger.com"
        assert er.username == "user"
        assert er.password == "pass"
        assert er.tcp_limit == 5
        assert er.sub_page_size == 4000
