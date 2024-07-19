import os
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from pydantic import SecretStr, ValidationError, validate_call

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ecoscope_workflows.annotations import EarthRangerClient
from ecoscope_workflows.connections import EarthRangerConnection


def test_connection_unnamed():
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

        assert isinstance(conn.password, SecretStr)
        assert str(conn.password) == "**********"
        assert conn.password.get_secret_value() == "pass"

        assert conn.tcp_limit == 5
        assert conn.sub_page_size == 4000


@pytest.fixture
def named_mock_env():
    return {
        "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__SERVER": (
            "https://mep-dev.pamdas.org"
        ),
        "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__USERNAME": "user",
        "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__PASSWORD": "pass",
        "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__TCP_LIMIT": "5",
        "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__SUB_PAGE_SIZE": "4000",
    }


def test_connection_named_from_env(named_mock_env):
    with patch.dict(os.environ, named_mock_env):
        conn = EarthRangerConnection.from_named_connection("MEP_DEV")
        assert conn.server == "https://mep-dev.pamdas.org"
        assert conn.username == "user"

        assert isinstance(conn.password, SecretStr)
        assert str(conn.password) == "**********"
        assert conn.password.get_secret_value() == "pass"

        assert conn.tcp_limit == 5
        assert conn.sub_page_size == 4000


@pytest.fixture
def mock_toml_config(tmp_path: Path):
    toml_config = dedent(
        """\
        [connections.earthranger.mep_dev]
        server = "https://mep-dev.pamdas.org"
        username = "user"
        password = "pass"
        tcp_limit = 5
        sub_page_size = 4000
        """
    )
    _ = tomllib.loads(toml_config)  # make sure toml string is loadable
    tmp_config_path = tmp_path / ".config.toml"
    tmp_config_path.write_text(toml_config)
    yield tmp_config_path


def test_connection_named_from_toml(mock_toml_config: Path):
    with patch("ecoscope_workflows.config.PATH", mock_toml_config):
        with patch.dict(os.environ, clear=True):
            conn = EarthRangerConnection.from_named_connection("mep_dev")
            assert conn.server == "https://mep-dev.pamdas.org"
            assert conn.username == "user"

            assert isinstance(conn.password, SecretStr)
            assert str(conn.password) == "**********"
            assert conn.password.get_secret_value() == "pass"

            assert conn.tcp_limit == 5
            assert conn.sub_page_size == 4000


@pytest.fixture
def mock_toml_config_no_secrets(tmp_path: Path):
    toml_config = dedent(
        """\
        [connections.earthranger.mep_dev]
        server = "https://mep-dev.pamdas.org"
        username = "user"
        tcp_limit = 5
        sub_page_size = 4000
        """
    )
    _ = tomllib.loads(toml_config)  # make sure toml string is loadable
    tmp_config_path = tmp_path / ".config.toml"
    tmp_config_path.write_text(toml_config)
    yield tmp_config_path


def test_connection_named_from_toml_with_env_secrets(mock_toml_config_no_secrets: Path):
    with patch.dict(os.environ, clear=True):
        with patch("ecoscope_workflows.config.PATH", mock_toml_config_no_secrets):
            with pytest.raises(ValidationError, match="password"):
                _ = EarthRangerConnection.from_named_connection("mep_dev")

        with patch("ecoscope_workflows.config.PATH", mock_toml_config_no_secrets):
            with patch.dict(
                os.environ,
                {
                    "ECOSCOPE_WORKFLOWS__CONNECTIONS__EARTHRANGER__MEP_DEV__PASSWORD": "pass"
                },
            ):
                conn = EarthRangerConnection.from_named_connection("mep_dev")
                assert conn.server == "https://mep-dev.pamdas.org"
                assert conn.username == "user"

                assert isinstance(conn.password, SecretStr)
                assert str(conn.password) == "**********"
                assert conn.password.get_secret_value() == "pass"

                assert conn.tcp_limit == 5
                assert conn.sub_page_size == 4000


def test_resolve_client_from_env(named_mock_env):
    @validate_call(config={"arbitrary_types_allowed": True})
    def f(client: EarthRangerClient):
        return client

    with patch.dict(os.environ, named_mock_env):
        with patch("ecoscope.io.EarthRangerIO", autospec=True):
            client = f(client="mep_dev")
            assert hasattr(client, "get_subjectgroup_observations")
            assert callable(client.get_subjectgroup_observations)


def test_resolve_client_from_toml(mock_toml_config: Path):
    @validate_call(config={"arbitrary_types_allowed": True})
    def f(client: EarthRangerClient):
        return client

    with patch("ecoscope_workflows.config.PATH", mock_toml_config):
        with patch("ecoscope.io.EarthRangerIO", autospec=True):
            client = f(client="mep_dev")
            assert hasattr(client, "get_subjectgroup_observations")
            assert callable(client.get_subjectgroup_observations)


@pytest.mark.xfail
def test_google_secrets_manager(): ...
