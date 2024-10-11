from typing import Annotated, ClassVar, Protocol, runtime_checkable

from pydantic import Field, SecretStr, field_validator
from pydantic.functional_validators import BeforeValidator
from pydantic.json_schema import WithJsonSchema

from ecoscope_workflows_core.annotations import AnyGeoDataFrame
from ecoscope_workflows_core.connections import DataConnection


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
    username: Annotated[str, Field(description="EarthRanger username")] = ""
    password: Annotated[SecretStr, Field(description="EarthRanger password")] = ""
    tcp_limit: Annotated[int, Field(description="TCP limit for API requests")]
    sub_page_size: Annotated[int, Field(description="Sub page size for API requests")]
    token: Annotated[SecretStr, Field(description="EarthRanger password")] = ""

    @field_validator("token")
    def token_or_password(cls, v, values):
        if not v and not (values["username"] and values["password"]):
            raise ValueError("EarthRanger username and password must be provided")

    def get_client(self) -> EarthRangerClientProtocol:
        from ecoscope.io import EarthRangerIO  # type: ignore[import-untyped]

        if self.token:
            return EarthRangerIO(
                server=self.server,
                existing_session=self.token.get_secret_value(),
                tcp_limit=self.tcp_limit,
                sub_page_size=self.sub_page_size,
            )
        else:
            return EarthRangerIO(
                server=self.server,
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
