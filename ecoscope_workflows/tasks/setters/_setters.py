from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@distributed
def set_groupers(
    groupers: Annotated[..., Field()],
):
    return groupers


@distributed
def set_map_styles(
    map_styles: Annotated[..., Field()],
):
    return map_styles
