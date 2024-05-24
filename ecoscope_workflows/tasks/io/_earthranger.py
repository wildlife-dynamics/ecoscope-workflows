import functools
import os
from datetime import datetime
from typing import Annotated, Any

import pandas as pd
import pandera as pa
from pydantic import Field
from pydantic.functional_validators import BeforeValidator

from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.annotations import DataFrame, JsonSerializableDataFrameModel


def from_env(_, var_name: str) -> str:
    """If no value is passed, load a value from the provided var_name."""
    value = os.environ.get(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not set.")
    return value


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


@distributed
def get_subjectgroup_observations(
    # client
    server: Annotated[
        str,
        Field(description="URL for EarthRanger API"),
        BeforeValidator(functools.partial(from_env, var_name="ER_SERVER")),
    ],
    username: Annotated[
        str,
        Field(description="EarthRanger username"),
        BeforeValidator(functools.partial(from_env, var_name="ER_USERNAME")),
    ],
    password: Annotated[
        str,
        Field(description="EarthRanger password"),
        BeforeValidator(functools.partial(from_env, var_name="ER_PASSWORD")),
    ],
    tcp_limit: Annotated[
        int, Field(description="TCP limit for EarthRanger API requests")
    ],
    sub_page_size: Annotated[
        int, Field(description="Sub page size for EarthRanger API requests")
    ],
    # get_subjectgroup_observations
    subject_group_name: Annotated[
        str, Field(description="Name of EarthRanger Subject")
    ],
    include_inactive: Annotated[
        bool, Field(description="Whether or not to include inactive subjects")
    ],
    since: Annotated[datetime, Field(description="Start date")],
    until: Annotated[datetime, Field(description="End date")],
) -> DataFrame[SubjectGroupObservationsGDFSchema]:
    from ecoscope.io import EarthRangerIO

    earthranger_io = EarthRangerIO(
        server=server,
        username=username,
        password=password,
        tcp_limit=tcp_limit,
        sub_page_size=sub_page_size,
    )
    return earthranger_io.get_subjectgroup_observations(
        subject_group_name=subject_group_name,
        include_subject_details=True,
        include_inactive=include_inactive,
        since=since,
        until=until,
    )
