from typing import Annotated

from pydantic import Field

from ecoscope_workflows.core.annotations import AnyGeoDataFrame
from ecoscope_workflows.core.decorators import task


@task
def get_day_night_ratio(
    df: AnyGeoDataFrame,
) -> Annotated[float, Field(description="Daynight ratio")]:
    from ecoscope.analysis import astronomy

    return astronomy.get_daynight_ratio(df)
