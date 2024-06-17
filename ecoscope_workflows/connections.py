from abc import ABC, abstractmethod
from typing import Annotated, Generic, Protocol, Type, TypeVar

from pydantic import Field
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import SettingsConfigDict

from ecoscope_workflows._settings import _Settings

DataConnectionType = TypeVar("DataConnectionType", bound="_DataConnection")
ClientProtocolType = TypeVar("ClientProtocolType")


class _DataConnection(_Settings):
    @classmethod
    def from_named_connection(
        cls: Type[DataConnectionType], name: str
    ) -> DataConnectionType:
        model_config = SettingsConfigDict(
            env_prefix=f"{name}_",
            case_sensitive=False,
            env_file=".env",
            env_file_encoding="utf-8",
        )
        _cls = type(
            f"{name}_connection",
            (cls,),
            {"model_config": model_config},
        )
        return _cls()


class DataConnection(ABC, _DataConnection, Generic[ClientProtocolType]):
    @abstractmethod
    def get_client(self) -> ClientProtocolType: ...

    @classmethod
    def client_from_named_connection(cls, name: str) -> ClientProtocolType:
        return cls.from_named_connection(name).get_client()


class EarthRangerClientProtocol(Protocol):
    def get_subjectgroup_observations(
        self,
        subject_group_name: str,
        include_subject_details: bool,
        include_inactive: bool,
        since,
        until,
    ) -> None: ...


class EarthRangerConnection(DataConnection[EarthRangerClientProtocol]):
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
    BeforeValidator(EarthRangerConnection.client_from_named_connection),
]
