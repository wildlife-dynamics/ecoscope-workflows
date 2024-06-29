from typing import Annotated

from pydantic import Field
import pandera as pa

from ecoscope_workflows.annotations import JsonSerializableDataFrameModel
from ecoscope_workflows.decorators import distributed


@distributed
def split_groups(
    dataframe: Annotated[pa.typing.DataFrame[JsonSerializableDataFrameModel], Field()],
    groupers: Annotated[list[str], Field()],
) -> Annotated[dict, Field()]:
    # FIXME: this can actually be .groupby(levels=[1, 2, 3]) if we have a heirarchical index
    return {k: v for k, v in dataframe.groupby(groupers)}
