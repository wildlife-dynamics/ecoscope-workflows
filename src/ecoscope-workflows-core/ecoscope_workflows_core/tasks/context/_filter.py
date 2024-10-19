from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from pydantic import Field

from ecoscope_workflows_core.decorators import task


@dataclass
class TimeFilter:
    since: datetime
    until: datetime
    time_format: str


@task
def time_filter(
    since, until, format: str
) -> Annotated[TimeFilter, Field(description="Time range filter")]:
    return TimeFilter(since=since, until=until, format=format)
