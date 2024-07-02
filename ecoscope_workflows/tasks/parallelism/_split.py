from typing import Annotated

from pydantic import Field
import pandera as pa

from ecoscope_workflows.annotations import JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed
from ecoscope_workflows.serde import (
    groupbykeys_to_hivekeys,
    persist_gdf_to_hive_partitioned_parquet,
)


@distributed
def split_groups(
    dataframe: Annotated[pa.typing.DataFrame[JsonSerializableDataFrameModel], Field()],
    groupers: Annotated[list[str], Field()],
    cache_path: Annotated[str, Field()],
) -> Annotated[list[dict[str, tuple[tuple[tuple[str, str, str], ...], str]]], Field()]:
    df_url = dataframe.pipe(
        persist_gdf_to_hive_partitioned_parquet,
        partition_on=groupers,
        path=cache_path,
    )
    return [
        {"element": (nested_hk, str(df_url))}
        for nested_hk in groupbykeys_to_hivekeys(dataframe, groupers)
        # {"element": ((('animal_name', '=', 'Bo'), ('month', '=', 'January')), "gcs://bucket/tmp/job-3456788/tmp.parquet")}
    ]
