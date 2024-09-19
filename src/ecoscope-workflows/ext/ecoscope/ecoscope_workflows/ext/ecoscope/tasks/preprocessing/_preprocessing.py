from typing import Annotated

import pandas as pd
import pandera as pa
import pandera.typing as pa_typing
from pydantic import Field

from ecoscope_workflows.core.annotations import DataFrame, GeoDataFrameBaseSchema
from ecoscope_workflows.core.decorators import task
from ecoscope_workflows.ext.ecoscope.tasks.io import SubjectGroupObservationsGDFSchema
from ecoscope_workflows.ext.ecoscope.tasks.transformation._filtering import Coordinate


class RelocationsGDFSchema(SubjectGroupObservationsGDFSchema):
    # FIXME: how does this differ from `SubjectGroupObservationsGDFSchema`?
    pass


@task
def process_relocations(
    observations: DataFrame[SubjectGroupObservationsGDFSchema],
    filter_point_coords: Annotated[list[Coordinate], Field()],
    relocs_columns: Annotated[list[str], Field()],
) -> DataFrame[RelocationsGDFSchema]:
    from ecoscope.base import Relocations, RelocsCoordinateFilter  # type: ignore[import-untyped]

    relocs = Relocations(observations)

    # filter relocations based on the config
    relocs.apply_reloc_filter(
        RelocsCoordinateFilter(
            filter_point_coords=[[coord.x, coord.y] for coord in filter_point_coords]
        ),
        inplace=True,
    )
    relocs.remove_filtered(inplace=True)

    # subset columns
    relocs = relocs[relocs_columns]

    # rename columns
    relocs.columns = [i.replace("extra__", "") for i in relocs.columns]
    relocs.columns = [i.replace("subject__", "") for i in relocs.columns]
    return relocs


class TrajectoryGDFSchema(GeoDataFrameBaseSchema):
    id: pa_typing.Index[str] = pa.Field()
    groupby_col: pa_typing.Series[str] = pa.Field()
    segment_start: pa_typing.Series[pd.DatetimeTZDtype] = pa.Field(
        dtype_kwargs={"unit": "ns", "tz": "UTC"}
    )
    segment_end: pa_typing.Series[pd.DatetimeTZDtype] = pa.Field(
        dtype_kwargs={"unit": "ns", "tz": "UTC"}
    )
    timespan_seconds: pa_typing.Series[float] = pa.Field()
    dist_meters: pa_typing.Series[float] = pa.Field()
    speed_kmhr: pa_typing.Series[float] = pa.Field()
    heading: pa_typing.Series[float] = pa.Field()
    junk_status: pa_typing.Series[bool] = pa.Field()


@task
def relocations_to_trajectory(
    relocations: DataFrame[RelocationsGDFSchema],
    min_length_meters: Annotated[float, Field()] = 0.1,
    max_length_meters: Annotated[float, Field()] = 10000,
    max_time_secs: Annotated[float, Field()] = 3600,
    min_time_secs: Annotated[float, Field()] = 1,
    max_speed_kmhr: Annotated[float, Field()] = 120,
    min_speed_kmhr: Annotated[float, Field()] = 0.0,
) -> DataFrame[TrajectoryGDFSchema]:
    from ecoscope.base import Relocations, Trajectory, TrajSegFilter

    # trajectory creation
    traj = Trajectory.from_relocations(Relocations(relocations))

    traj_seg_filter = TrajSegFilter(
        min_length_meters=min_length_meters,
        max_length_meters=max_length_meters,
        min_time_secs=min_time_secs,
        max_time_secs=max_time_secs,
        min_speed_kmhr=min_speed_kmhr,
        max_speed_kmhr=max_speed_kmhr,
    )

    # trajectory filtering
    traj.apply_traj_filter(traj_seg_filter, inplace=True)
    traj.remove_filtered(inplace=True)

    return traj
