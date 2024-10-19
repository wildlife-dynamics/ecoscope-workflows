from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from pydantic import Field

from ecoscope_workflows_core.decorators import task


@dataclass
class TimeRange:
    since: datetime
    until: datetime
    time_format: str


@task
def set_time_range(
    since, until, format: str
) -> Annotated[TimeRange, Field(description="Time range filter")]:
    return TimeRange(since=since, until=until, format=format)
