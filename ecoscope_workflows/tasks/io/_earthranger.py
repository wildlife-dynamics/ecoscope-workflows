from datetime import datetime
from typing import Annotated, Any

import pandas as pd
import pandera as pa
from pydantic import Field

from ecoscope_workflows.annotations import (
    DataFrame,
    EarthRangerClient,
    JsonSerializableDataFrameModel,
)
from ecoscope_workflows.decorators import distributed


class SubjectGroupObservationsGDFSchema(JsonSerializableDataFrameModel):
    geometry: pa.typing.Series[Any] = (
        pa.Field()
    )  # see note in tasks/time_density re: geometry typing
    groupby_col: pa.typing.Series[object] = pa.Field()
    fixtime: pa.typing.Series[pd.DatetimeTZDtype] = pa.Field(
        dtype_kwargs={"unit": "ns", "tz": "UTC"}
    )
    junk_status: pa.typing.Series[bool] = pa.Field()
    # TODO: can we be any more specific about the `extra__` field expectations?


class EventGDFSchema(JsonSerializableDataFrameModel):
    geometry: pa.typing.Series[Any] = pa.Field()
    id: pa.typing.Series[str] = pa.Field()
    event_type: pa.typing.Series[str] = pa.Field()


@distributed(tags=["io"])
def get_subjectgroup_observations(
    client: EarthRangerClient,
    subject_group_name: Annotated[
        str, Field(description="Name of EarthRanger Subject")
    ],
    since: Annotated[datetime, Field(description="Start date")],
    until: Annotated[datetime, Field(description="End date")],
    include_inactive: Annotated[
        bool,
        Field(description="Whether or not to include inactive subjects"),
    ] = True,
) -> DataFrame[SubjectGroupObservationsGDFSchema]:
    """Get observations for a subject group from EarthRanger."""
    return client.get_subjectgroup_observations(
        subject_group_name=subject_group_name,
        include_subject_details=True,
        include_inactive=include_inactive,
        since=since,
        until=until,
    )


@distributed(tags=["io"])
def get_patrol_observations(
    client: EarthRangerClient,
    since: Annotated[str, Field(description="Start date")],
    until: Annotated[str, Field(description="End date")],
    patrol_type: Annotated[
        list[str],
        Field(description="list of UUID of patrol types"),
    ],
    status: Annotated[
        list[str],
        Field(
            description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'",
        ),
    ],
    include_patrol_details: Annotated[
        bool, Field(default=False, description="Include patrol details")
    ] = False,
) -> DataFrame[SubjectGroupObservationsGDFSchema]:
    """Get observations for a patrol type from EarthRanger."""
    return client.get_patrol_observations_with_patrol_filter(
        since=since,
        until=until,
        patrol_type=patrol_type,
        status=status,
        include_patrol_details=include_patrol_details,
    )


@distributed(tags=["io"])
def get_patrol_events(
    client: EarthRangerClient,
    since: Annotated[str, Field(description="Start date")],
    until: Annotated[str, Field(description="End date")],
    patrol_type: Annotated[
        list[str],
        Field(description="list of UUID of patrol types"),
    ],
    status: Annotated[
        list[str],
        Field(
            description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'",
        ),
    ],
) -> DataFrame[EventGDFSchema]:
    """Get events from patrols."""
    return client.get_patrol_events(
        since=since,
        until=until,
        patrol_type=patrol_type,
        status=status,
    )
