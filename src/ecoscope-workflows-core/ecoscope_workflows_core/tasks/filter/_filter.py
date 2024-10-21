from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from pydantic import Field

from ecoscope_workflows_core.decorators import task


@dataclass
class TimeRange:
    since: datetime
    until: datetime
    time_format: str = "%d %b %Y %H:%M:%S %Z"


@task
def set_time_range(
    since: Annotated[datetime, Field(description="The start time")],
    until: Annotated[datetime, Field(description="The end time")],
    time_format: Annotated[str, Field(description="The time format")],
) -> Annotated[TimeRange, Field(description="Time range filter")]:
    return TimeRange(since=since, until=until, time_format=time_format)
