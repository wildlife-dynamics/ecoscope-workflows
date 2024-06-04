from dataclasses import dataclass


@dataclass
class Groupers:
    a: ...
    b: ...
    c: ...


@dataclass(frozen=True)
class GroupKey:
    a: str | None
    b: str | None
    c: str | None


@dataclass
class SingleValue:
    value: int | float


@dataclass
class Map:
    path: str


@dataclass
class PerGroupPatrolReportDashboard:
    mean_time: dict[GroupKey, SingleValue]
    total_time: dict[GroupKey, SingleValue]
    total_distance: dict[GroupKey, SingleValue]
    mean_distance: dict[GroupKey, SingleValue]
    trajectory_map: dict[GroupKey, Map]
    time_density: ...  # does not have a group key
