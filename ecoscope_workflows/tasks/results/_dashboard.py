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
    mean_time: dict[GroupKey, SingleValue]
    total_time: dict[GroupKey, SingleValue]
    total_distance: dict[GroupKey, SingleValue]
    mean_distance: dict[GroupKey, SingleValue]
    trajectory_map: dict[GroupKey, Map]
    time_density_map: Map
    # events results


@distributed
def make_patrols_dashboard(
    trajectory_grouped_single_values: dict[str, dict[GroupKey, SingleValue]],
    trajectory_grouped_maps: dict[GroupKey, Map],
    time_density_map: Map,
    events_grouped_plots: dict[GroupKey, Plot],
    events_non_grouped_plot: Plot,
) -> PerGroupPatrolReportDashboard:
    groupers: Groupers = ...  # infer groupers from grouped data indexes here
    return PerGroupPatrolReportDashboard(
        groupers=groupers,
        # trajectories results
        mean_time=trajectory_grouped_single_values["mean_time"],
        total_time=trajectory_grouped_single_values["total_time"],
        total_distance=trajectory_grouped_single_values["total_distance"],
        mean_distance=trajectory_grouped_single_values["mean_distance"],
        trajectory_grouped_maps=trajectory_grouped_maps,
        # NOTE: use null GroupKey to store non-grouped results
        time_density_map={GroupKey(): time_density_map},
        # events results
        events_grouped_plots=events_grouped_plots,
        events_non_grouped_plot={GroupKey(): events_non_grouped_plot},
    )
