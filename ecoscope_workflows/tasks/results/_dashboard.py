from dataclasses import dataclass
from typing import Generic, TypeVar

from ecoscope_workflows.decorators import distributed


@dataclass
class Groupers:
    a: ...
    b: ...
    c: ...


@dataclass(frozen=True)
class GroupKey:
    a: str | None = None
    b: str | None = None
    c: str | None = None


@dataclass
class SingleValue:
    value: int | float


@dataclass
class Map:
    path: str


@dataclass
class Plot:
    path: str


@dataclass
class Table: ...


@dataclass
class StaticImage:
    path: str


@dataclass
class Calendar: ...


@dataclass
class Text:
    text: str


Result = TypeVar("Result", SingleValue, Map, Plot, Table, StaticImage, Calendar, Text)


@dataclass
class KeyedResult(Generic[Result]):
    key: GroupKey
    result: Result


@dataclass
class PerGroupPatrolReportDashboard:
    groupers: Groupers
    # trajectories results
    mean_times: list[KeyedResult[SingleValue]]
    total_times: list[KeyedResult[SingleValue]]
    total_distances: list[KeyedResult[SingleValue]]
    mean_distances: list[KeyedResult[SingleValue]]
    trajectory_maps: list[KeyedResult[Map]]
    time_density_map: Map
    # events results
    events_grouped_plots: list[KeyedResult[Plot]]
    events_ungrouped_plot: Plot


@distributed
def make_patrols_dashboard(
    trajectory_grouped_single_values: dict[str, KeyedResult[SingleValue]],
    trajectory_grouped_maps: KeyedResult[Map],
    time_density_map: Map,
    events_grouped_plots: list[KeyedResult[Plot]],
    events_ungrouped_plot: Plot,
) -> PerGroupPatrolReportDashboard:
    groupers: Groupers = ...  # infer groupers from grouped data indexes here
    return PerGroupPatrolReportDashboard(
        groupers=groupers,
        **trajectory_grouped_single_values,
        trajectory_grouped_maps=trajectory_grouped_maps,
        time_density_map=time_density_map,
        events_grouped_plots=events_grouped_plots,
        events_ungrouped_plot=events_ungrouped_plot,
    )
