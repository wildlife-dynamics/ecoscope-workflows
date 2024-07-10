from typing import Annotated, TypedDict

from pydantic import Field
import pandera as pa

from ecoscope_workflows.annotations import JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import (
    CompositeFilter,
    groupbykeys_to_hivekeys,
    persist_gdf_to_hive_partitioned_parquet,
)


class Groups(TypedDict):
    widget_name: str
    widget_kws: dict
    path: str
    filters: CompositeFilter


@distributed
def split_groups(
    widget_name: Annotated[str, Field()],
    widget_kws: Annotated[dict, Field()],
    dataframe: Annotated[pa.typing.DataFrame[JsonSerializableDataFrameModel], Field()],
    groupers: Annotated[list[str], Field()],
    cache_path: Annotated[str, Field()],
) -> Annotated[list[Groups], Field()]:
    df_url = dataframe.pipe(
        persist_gdf_to_hive_partitioned_parquet,
        partition_on=groupers,
        path=cache_path,
    )
    return [
        {
            "widget_name": widget_name,
            "widget_kws": widget_kws,
            "path": str(df_url),
            "filters": nested_hk,
        }
        for nested_hk in groupbykeys_to_hivekeys(dataframe, groupers)
        # {
        #   "widget_name": "time_density_ecomap",
        #   "widget_kws": {...},
        #   "path": "gcs://bucket/tmp/job-3456788/tmp.parquet",
        #   "filters": (('animal_name', '=', 'Bo'), ('month', '=', 'January')),
        # }
    ]
