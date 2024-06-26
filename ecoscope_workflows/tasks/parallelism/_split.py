from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@distributed
def split_groups(
    dataframe: Annotated[..., Field()],
    groupers: Annotated[..., Field()],
): ...
