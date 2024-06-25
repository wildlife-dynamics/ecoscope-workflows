from typing import Annotated
from dataclasses import dataclass

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@dataclass
class Dashboard:
    groupers: list
    widgets: list

    @property
    def views(self): ...


@distributed
def gather_dashboard(
    widgets: Annotated[list, Field()],
    groupers: Annotated[list, Field()],
):
    return Dashboard(groupers=groupers, widgets=widgets)
