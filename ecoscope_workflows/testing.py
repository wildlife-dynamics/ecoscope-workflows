from dataclasses import dataclass
from typing import Callable, Literal, Protocol
from unittest.mock import MagicMock, create_autospec

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from ecoscope_workflows.util import (
    load_example_return_from_task_reference,
    import_distributed_task_from_reference,
)


class MockWrappedFunctionProtocol(Protocol):
    return_value: MagicMock

    def __call__(self, *args, **kws):
        """Mocks the call signature of a function decorated by `@distributed`.
        These functions can have arbitrary signatures, so we use `*args` and `**kws`.
        """
        ...


class MockReplaceProtocol(Protocol):
    return_value: MockWrappedFunctionProtocol

    def __call__(
        self,
        arg_prevalidators: dict[str, Callable] | None = None,
        return_postvalidator: Callable | None = None,
        validate: bool | None = None,
    ) -> "DistributedTaskMagicMock":
        """Mocks the call signature of `distributed.replace`, which returns a mutated
        instance of the `distributed` decorator with the specified changes.
        """
        ...


class DistributedTaskMagicMock(MagicMock):
    replace: MockReplaceProtocol


def create_distributed_task_magicmock(
    anchor: str, func_name: str
) -> DistributedTaskMagicMock:
    spec = import_distributed_task_from_reference(anchor, func_name)
    mock_task: DistributedTaskMagicMock = create_autospec(spec=spec)
    # match the signature of the wrapped function, to require same arguments
    mock_task.replace.return_value = create_autospec(spec=spec.func)
    # load the example return data
    example_return = load_example_return_from_task_reference(anchor, func_name)
    mock_task.replace.return_value.return_value = example_return
    return mock_task


@dataclass
class BoundingBox:
    min_x: float
    max_x: float
    min_y: float
    max_y: float


def _generate_random_2d_walk_coordinates(
    num_fixes: int, bbox: BoundingBox, seed: int
) -> list[Point]:
    np.random.seed(seed)

    coords = np.zeros((num_fixes, 2))
    coords[0] = np.random.uniform(
        [bbox.min_x, bbox.min_y], [bbox.max_x, bbox.max_y]
    )  # Start point

    for i in range(1, num_fixes):
        step_x = np.random.uniform(-0.1, 0.1)  # Small random steps
        step_y = np.random.uniform(-0.1, 0.1)
        new_x = np.clip(coords[i - 1, 0] + step_x, bbox.min_x, bbox.max_x)
        new_y = np.clip(coords[i - 1, 1] + step_y, bbox.min_y, bbox.max_y)
        coords[i] = [new_x, new_y]

    return [Point(x, y) for x, y in coords]


def generate_synthetic_gps_fixes_dataframe(
    num_fixes: int = 1000,
    start_time: pd.Timestamp = pd.Timestamp("2023-01-01 00:00:00"),
    time_interval_minutes: int = 10,
    seed: int = 42,
    animal_type: str = "Elephant",
    animal_names: list[str] = ["Bo", "Mo", "Jo"],
    bbox: BoundingBox = BoundingBox(-5, 5, -5, 5),
    crs: str = "EPSG:4326",
    social_structure: Literal["solitary", "group"] = "solitary",
) -> gpd.GeoDataFrame:
    fix_times = pd.date_range(
        start=start_time,
        periods=num_fixes,
        freq=f"{time_interval_minutes}T",
        tz="UTC",
    )
    # Generate random 2D walk coordinates within the bounding box
    geometry = []
    for i in range(len(animal_names)):
        geometry += _generate_random_2d_walk_coordinates(num_fixes, bbox, seed=seed + i)

    nrows = num_fixes * len(animal_names)
    if social_structure == "group":
        # randomly assign each fix to an animal, the animals will move adjacent to one another
        animal_name = [np.random.choice(animal_names) for _ in range(nrows)]
    elif social_structure == "solitary":
        # each animal moves independently on its own trajectory
        animal_name = [name for name in animal_names for _ in range(num_fixes)]

    return gpd.GeoDataFrame(
        {
            "animal_type": [animal_type] * nrows,
            "animal_name": animal_name,
            "fixtime": list(fix_times) * len(animal_names),
            "geometry": geometry,
            "junk_status": [False] * nrows,
            "groupby_col": ["group"] * nrows,
        },
        geometry="geometry",
        crs=crs,
    )
