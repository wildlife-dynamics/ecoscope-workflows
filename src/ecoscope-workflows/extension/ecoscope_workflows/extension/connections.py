from typing import Annotated, ClassVar, Protocol, runtime_checkable

from pydantic import Field, SecretStr
from pydantic.functional_validators import BeforeValidator
from pydantic.json_schema import WithJsonSchema

from ecoscope_workflows.core.annotations import AnyGeoDataFrame
from ecoscope_workflows.core.connections import DataConnection


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


EarthRangerClient = Annotated[
    EarthRangerClientProtocol,
    BeforeValidator(EarthRangerConnection.client_from_named_connection),
    WithJsonSchema(
        {"type": "string", "description": "A named EarthRanger connection."}
    ),
]
