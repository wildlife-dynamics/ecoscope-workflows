from abc import ABC, abstractmethod
from inspect import ismethod
from typing import (
    Annotated,
    ClassVar,
    Generic,
    Protocol,
    Type,
    TypeVar,
    get_args,
    runtime_checkable,
)

from pydantic import Field, SecretStr
from pydantic.functional_validators import BeforeValidator
from pydantic.json_schema import WithJsonSchema
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

import ecoscope_workflows.core.config as config
from ecoscope_workflows.core.annotations import AnyGeoDataFrame


class _Settings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            PyprojectTomlConfigSettingsSource(settings_cls, toml_file=config.PATH),
            # dotenv_settings,
            # file_secret_settings,
        )


DataConnectionType = TypeVar("DataConnectionType", bound="DataConnection")
ClientProtocolType = TypeVar("ClientProtocolType")


class _DataConnection(_Settings):
    @classmethod
    def from_named_connection(  # type: ignore[misc]
        cls: Type[DataConnectionType], name: str
    ) -> DataConnectionType:
        model_config = SettingsConfigDict(
            env_prefix=(
                "ecoscope_workflows__connections__"
                f"{cls.__ecoscope_connection_type__}__{name.lower()}__"
            ),
            case_sensitive=False,
            pyproject_toml_table_header=(
                "connections",
                cls.__ecoscope_connection_type__,
                name,
            ),
        )
        _cls = type(
            f"{name}_connection",
            (cls,),
            {"model_config": model_config},
        )
        return _cls()


class DataConnection(ABC, _DataConnection, Generic[ClientProtocolType]):
    __ecoscope_connection_type__: ClassVar[str] = NotImplemented

    @abstractmethod
    def get_client(self) -> ClientProtocolType: ...

    # @abstractmethod
    # def check_connection(self) -> None: ...

    @classmethod
    def client_from_named_connection(cls, name: str) -> ClientProtocolType:
        return cls.from_named_connection(name).get_client()


@runtime_checkable
class EarthRangerClientProtocol(Protocol):
    def get_subjectgroup_observations(
        self,
        subject_group_name: str,
        include_subject_details: bool,
        include_inactive: bool,
        since,
        until,
    ) -> AnyGeoDataFrame: ...

    def get_patrol_observations_with_patrol_filter(
        self,
        since,
        until,
        patrol_type,
        status,
        include_patrol_details,
    ) -> AnyGeoDataFrame: ...

    def get_patrol_events(
        self,
        since,
        until,
        patrol_type,
        status,
    ) -> AnyGeoDataFrame: ...


class EarthRangerConnection(DataConnection[EarthRangerClientProtocol]):
    __ecoscope_connection_type__: ClassVar[str] = "earthranger"

    server: Annotated[str, Field(description="EarthRanger API URL")]
    username: Annotated[str, Field(description="EarthRanger username")]
    password: Annotated[SecretStr, Field(description="EarthRanger password")]
    tcp_limit: Annotated[int, Field(description="TCP limit for API requests")]
    sub_page_size: Annotated[int, Field(description="Sub page size for API requests")]

    def get_client(self) -> EarthRangerClientProtocol:
        from ecoscope.io import EarthRangerIO  # type: ignore[import-untyped]

        return EarthRangerIO(
            server=self.server,
            # TODO: token-based authentication
            username=self.username,
            password=self.password.get_secret_value(),
            tcp_limit=self.tcp_limit,
            sub_page_size=self.sub_page_size,
        )


def is_client(obj):
    if hasattr(obj, "__origin__") and hasattr(obj, "__args__"):
        if any(isinstance(arg, BeforeValidator) for arg in get_args(obj)):
            bv = [arg for arg in get_args(obj) if isinstance(arg, BeforeValidator)][0]
            if ismethod(bv.func) and bv.func.__name__ == "client_from_named_connection":
                return True
    return False


def connection_from_client(obj) -> DataConnection:
    assert is_client(obj)
    bv = [arg for arg in get_args(obj) if isinstance(arg, BeforeValidator)][0]
    conn_type = bv.func.__self__  # type: ignore[union-attr]
    assert issubclass(conn_type, DataConnection)
    return conn_type


EarthRangerClient = Annotated[
    EarthRangerClientProtocol,
    BeforeValidator(EarthRangerConnection.client_from_named_connection),
    WithJsonSchema(
        {"type": "string", "description": "A named EarthRanger connection."}
    ),
]
