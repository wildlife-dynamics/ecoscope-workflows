from datetime import datetime
from typing import Annotated, Literal, cast

import pandas as pd
import pandera as pa
import pandera.typing as pa_typing
from pydantic import Field

from ecoscope_workflows.annotations import DataFrame, GeoDataFrameBaseSchema
from ecoscope_workflows.connections import EarthRangerClient
from ecoscope_workflows.decorators import task


class SubjectGroupObservationsGDFSchema(GeoDataFrameBaseSchema):
    groupby_col: pa_typing.Series[str] = pa.Field()
    fixtime: pa_typing.Series[pd.DatetimeTZDtype] = pa.Field(
        dtype_kwargs={"unit": "ns", "tz": "UTC"}
    )
    junk_status: pa_typing.Series[bool] = pa.Field()
    # TODO: can we be any more specific about the `extra__` field expectations?


class EventGDFSchema(GeoDataFrameBaseSchema):
    id: pa_typing.Series[str] = pa.Field()
    event_type: pa_typing.Series[str] = pa.Field()


@task(tags=["io"])
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
    return cast(
        DataFrame[SubjectGroupObservationsGDFSchema],
        client.get_subjectgroup_observations(
            subject_group_name=subject_group_name,
            include_subject_details=True,
            include_inactive=include_inactive,
            since=since,
            until=until,
        ),
    )


@task(tags=["io"])
def get_patrol_observations(
    client: EarthRangerClient,
    since: Annotated[str, Field(description="Start date")],
    until: Annotated[str, Field(description="End date")],
    patrol_type: Annotated[
        list[str],
        Field(description="list of UUID of patrol types"),
    ],
    status: Annotated[
        list[Literal["active", "overdue", "done", "cancelled"]],
        Field(description="list of 'scheduled'/'active'/'overdue'/'done'/'cancelled'"),
    ],
    include_patrol_details: Annotated[
        bool, Field(default=False, description="Include patrol details")
    ] = False,
) -> DataFrame[SubjectGroupObservationsGDFSchema]:
    """Get observations for a patrol type from EarthRanger."""
    return cast(
        DataFrame[SubjectGroupObservationsGDFSchema],
        client.get_patrol_observations_with_patrol_filter(
            since=since,
            until=until,
            patrol_type=patrol_type,
            status=status,
            include_patrol_details=include_patrol_details,
        ),
    )


@task(tags=["io"])
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
    return cast(
        DataFrame[EventGDFSchema],
        client.get_patrol_events(
            since=since,
            until=until,
            patrol_type=patrol_type,
            status=status,
        ),
    )
