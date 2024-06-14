import functools
from abc import ABC
from typing import Annotated, Protocol

from pydantic import Field
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import SettingsConfigDict

from ecoscope_workflows.settings import Settings


class DataConnection(ABC, type):
    def get_client(self): ...


def client_from_named_connection(
    name: str, conn_type: DataConnection
) -> DataConnection:
    connection = type(
        f"{name}_connection",
        (conn_type,),
        {
            "model_config": SettingsConfigDict(
                env_prefix=f"{name}_",
                case_sensitive=False,
                env_file=".env",
                env_file_encoding="utf-8",
            ),
        },
    )
    return connection().get_client()


class EarthRangerClientProtocol(Protocol):
    def get_subjectgroup_observations(
        self,
        subject_group_name: str,
        include_subject_details: bool,
        include_inactive: bool,
        since,
        until,
    ) -> None: ...


class EarthRangerConnection(Settings, DataConnection):
    server: Annotated[str, Field(description="URL for EarthRanger API")]
    username: Annotated[str, Field(description="EarthRanger username")]
    password: Annotated[str, Field(description="EarthRanger password")]
    tcp_limit: Annotated[int, Field(description="TCP limit for API requests")]
    sub_page_size: Annotated[int, Field(description="Sub page size for API requests")]

    def get_client(self) -> EarthRangerClientProtocol:
        from ecoscope.io import EarthRangerIO

        return EarthRangerIO(
            server=self.server,
            # TODO: token-based authentication
            username=self.username,
            password=self.password,
            tcp_limit=self.tcp_limit,
            sub_page_size=self.sub_page_size,
        )


EarthRangerClient = Annotated[
    EarthRangerClientProtocol,
    BeforeValidator(
        functools.partial(
            client_from_named_connection, conn_type=EarthRangerConnection
        ),
    ),
]
