from datetime import datetime
from typing import Annotated, Any

import pandas as pd
import pandera as pa
from pydantic import Field

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.connections import EarthRangerClient
from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel


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


@distributed(tags=["io"])
def get_subjectgroup_observations(
    client: EarthRangerClient,
    subject_group_name: Annotated[
        str, Field(description="Name of EarthRanger Subject")
    ],
    include_inactive: Annotated[
        bool,
        Field(description="Whether or not to include inactive subjects"),
    ],
    since: Annotated[datetime, Field(description="Start date")],
    until: Annotated[datetime, Field(description="End date")],
) -> DataFrame[SubjectGroupObservationsGDFSchema]:
    """Get observations for a subject group from EarthRanger."""
    return client.get_subjectgroup_observations(
        subject_group_name=subject_group_name,
        include_subject_details=True,
        include_inactive=include_inactive,
        since=since,
        until=until,
    )
