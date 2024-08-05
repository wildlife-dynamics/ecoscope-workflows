from importlib.resources import files

import pytest

from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.results._ecomap import draw_ecomap
from ecoscope_workflows.tasks.results._map_config import (
    PathLayerProperty,
    ScatterPlotLayerProperty,
)


@pytest.fixture
def relocations():
    return gpd_from_parquet_uri(
        str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "process-relocations.example-return.parquet"
        )
    )


@pytest.fixture
def trajectories():
    return gpd_from_parquet_uri(
        str(
            files("ecoscope_workflows.tasks.preprocessing")
            / "relocations-to-trajectory.example-return.parquet"
        )
    )


def test_draw_ecomap_points(relocations):
    map_html = draw_ecomap(
        geodataframe=relocations,
        data_type="Scatterplot",
        style_props=ScatterPlotLayerProperty(
            get_radius=700, get_fill_color=[0, 255, 255]
        ),
        tile_layer="OpenStreetMap",
        title="Relocations",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_lines(trajectories):
    map_html = draw_ecomap(
        geodataframe=trajectories,
        data_type="Path",
        style_props=PathLayerProperty(get_width=200, get_color=[0, 255, 255]),
        tile_layer="OpenStreetMap",
        title="Trajectories",
    )
    assert isinstance(map_html, str)
