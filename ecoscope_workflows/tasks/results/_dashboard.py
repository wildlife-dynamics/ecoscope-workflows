from typing import Annotated
from dataclasses import dataclass

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@dataclass
class Dashboard:
    groupers: ...
    widgets: ...

    @property
    def views(self): ...


@distributed
def gather_dashboard(
    widgets: Annotated[..., Field()],
    groupers: Annotated[..., Field()],
):
    return Dashboard(groupers=groupers, widgets=widgets)
