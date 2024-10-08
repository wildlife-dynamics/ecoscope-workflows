from abc import ABC, abstractmethod
from inspect import ismethod
from typing import ClassVar, Generic, Type, TypeVar, get_args

from pydantic.functional_validators import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


DataConnectionType = TypeVar("DataConnectionType", bound="DataConnection")
ClientProtocolType = TypeVar("ClientProtocolType")


class _DataConnection(BaseSettings):
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
