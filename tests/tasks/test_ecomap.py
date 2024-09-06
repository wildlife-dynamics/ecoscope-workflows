from importlib.resources import files

import pytest

from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.results._ecomap import (
    PointLayerStyle,
    PolylineLayerStyle,
    create_map_layer,
    draw_ecomap,
)

pytestmark = pytest.mark.requires_ecoscope_core


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
    geo_layer = create_map_layer(
        geodataframe=relocations,
        layer_style=PointLayerStyle(get_radius=150, get_fill_color="#0000FF"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layer="OpenStreetMap",
        title="Relocations",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_lines(trajectories):
    geo_layer = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=200, get_color="#00FFFF"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layer="OpenStreetMap",
        title="Trajectories",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_combined(relocations, trajectories):
    relocs = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=200, get_color="#00FFFF"),
    )
    traj = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=200, get_color="#00FFFF"),
    )

    map_html = draw_ecomap(
        geo_layers=[relocs, traj],
        tile_layer="OpenStreetMap",
        title="Relocations and Trajectories",
    )
    assert isinstance(map_html, str)
    map_html = draw_ecomap(
        geo_layers=[relocs, traj],
        tile_layer="OpenStreetMap",
        title="Relocations and Trajectories",
    )
    assert isinstance(map_html, str)
    assert isinstance(map_html, str)
