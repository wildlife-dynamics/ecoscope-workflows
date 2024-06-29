from typing import Annotated, Any
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


@distributed
def gather_widget(
    content: Annotated[list[tuple[tuple, Any]], Field()],
    widget_type: Annotated[str, Field()] = "ecomap",
    title: Annotated[str, Field()] = "Time Density Ecomap",
):
    if widget_type == "ecomap":
        return {
            "widget_type": "ecomap",
            "views": {c[0]: c[1] for c in content},
            "title": title,
        }
    else:
        raise NotImplementedError(f"Unknown widget type: {widget_type}")
