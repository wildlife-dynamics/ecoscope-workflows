from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

from ecoscope_workflows.config import TomlConfigTable


def test_toml_config_table_dumps():
    tct = TomlConfigTable(
        header="connections",
        subheader="earthranger",
        name="mep_dev",
        fields={
            "server": "https://mep-dev.pamdas.org",
            "username": "user",
            "password": "pass",
            "tcp_limit": 5,
            "sub_page_size": 4000,
        },
    )
    assert tct.dumps() == dedent(
        """\
        [connections.earthranger.mep_dev]
        server = "https://mep-dev.pamdas.org"
        username = "user"
        password = "pass"
        tcp_limit = 5
        sub_page_size = 4000
        """
    )


def test_toml_config_table_dump(tmp_path: Path):
    tct = TomlConfigTable(
        header="connections",
        subheader="earthranger",
        name="mep_dev",
        fields={
            "server": "https://mep-dev.pamdas.org",
            "username": "user",
            "password": "pass",
            "tcp_limit": 5,
            "sub_page_size": 4000,
        },
    )
    tmp_config_path = tmp_path / ".config.toml"
    with patch("ecoscope_workflows.config.PATH", tmp_config_path):
        tct.dump()
        assert tmp_config_path.read_text() == dedent(
            """\
            [connections.earthranger.mep_dev]
            server = "https://mep-dev.pamdas.org"
            username = "user"
            password = "pass"
            tcp_limit = 5
            sub_page_size = 4000
            """
        )


def test_toml_config_table_add_and_delete(tmp_path: Path):
    tct0 = TomlConfigTable(
        header="connections",
        subheader="earthranger",
        name="mep_dev",
        fields={
            "server": "https://mep-dev.pamdas.org",
            "username": "user",
            "password": "pass",
            "tcp_limit": 5,
            "sub_page_size": 4000,
        },
    )
    tct1 = TomlConfigTable(
        header="connections",
        subheader="earthranger",
        name="amboseli",
        fields={
            "server": "https://amb.pamdas.org",
            "username": "user",
            "password": "pass",
            "tcp_limit": 3,
            "sub_page_size": 1000,
        },
    )
    tmp_config_path = tmp_path / ".config.toml"
    with patch("ecoscope_workflows.config.PATH", tmp_config_path):
        tct0.dump()
        tct1.dump()

        assert tmp_config_path.read_text() == dedent(
            """\
            [connections.earthranger.mep_dev]
            server = "https://mep-dev.pamdas.org"
            username = "user"
            password = "pass"
            tcp_limit = 5
            sub_page_size = 4000

            [connections.earthranger.amboseli]
            server = "https://amb.pamdas.org"
            username = "user"
            password = "pass"
            tcp_limit = 3
            sub_page_size = 1000
            """
        )

        tct0.delete()
        tmp_config_path.read_text() == dedent(
            """\
            [connections.earthranger.amboseli]
            server = "https://amb.pamdas.org"
            username = "user"
            password = "pass"
            tcp_limit = 3
            sub_page_size = 1000
            """
        )
