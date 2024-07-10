import pytest
from importlib.resources import files
from ecoscope_workflows.serde import gpd_from_parquet_uri
from ecoscope_workflows.tasks.results._ecomap import draw_ecomap


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
        style_kws={"get_radius": 700, "get_fill_color": "#00FFFF"},
        tile_layer="OpenStreetMap",
        title="Relocations",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_lines(trajectories):
    map_html = draw_ecomap(
        geodataframe=trajectories,
        data_type="Path",
        style_kws={"get_width": 200, "get_color": "#00FFFF"},
        tile_layer="OpenStreetMap",
        title="Trajectories",
    )
    assert isinstance(map_html, str)
