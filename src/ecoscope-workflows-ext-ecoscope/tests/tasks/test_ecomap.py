from importlib.resources import files

import pytest
from ecoscope_workflows_core.serde import gpd_from_parquet_uri
from ecoscope_workflows_ext_ecoscope.tasks.results._ecomap import (
    LegendDefinition,
    LegendStyle,
    NorthArrowStyle,
    PointLayerStyle,
    PolylineLayerStyle,
    TileLayer,
    create_map_layer,
    draw_ecomap,
)


@pytest.fixture
def relocations():
    return gpd_from_parquet_uri(
        str(
            files("ecoscope_workflows_ext_ecoscope.tasks.preprocessing")
            / "process-relocations.example-return.parquet"
        )
    )


@pytest.fixture
def trajectories():
    return gpd_from_parquet_uri(
        str(
            files("ecoscope_workflows_ext_ecoscope.tasks.preprocessing")
            / "relocations-to-trajectory.example-return.parquet"
        )
    )


@pytest.fixture
def trajectories_colored(trajectories):
    # mock the output of 'apply_classification'
    trajectories["speed_bins"] = trajectories["speed_kmhr"].apply(
        lambda x: "Fast" if x > 0.5 else "Slow"
    )
    # mock the output of 'apply_colormap'
    trajectories["colors"] = trajectories["speed_kmhr"].apply(
        lambda x: (255, 0, 0, 255) if x > 0.5 else (0, 255, 0, 255)
    )
    return trajectories


def test_draw_ecomap_points(relocations):
    geo_layer = create_map_layer(
        geodataframe=relocations,
        layer_style=PointLayerStyle(get_radius=15, get_fill_color="#0000FF"),
    )
    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Relocations",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_lines(trajectories):
    geo_layer = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=20, get_color="#00FFFF"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Trajectories",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_combined(relocations, trajectories):
    relocs = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=20, get_color="#00FFFF"),
    )
    traj = create_map_layer(
        geodataframe=trajectories,
        layer_style=PolylineLayerStyle(get_width=20, get_color="#00FFFF"),
    )

    map_html = draw_ecomap(
        geo_layers=[relocs, traj],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Relocations and Trajectories",
    )
    assert isinstance(map_html, str)
    map_html = draw_ecomap(
        geo_layers=[relocs, traj],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Relocations and Trajectories",
    )
    assert isinstance(map_html, str)
    assert isinstance(map_html, str)


def test_draw_ecomap_with_colormap(trajectories_colored):
    geo_layer = create_map_layer(
        geodataframe=trajectories_colored,
        layer_style=PolylineLayerStyle(get_width=20, color_column="colors"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Trajectories",
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_with_legend(trajectories_colored):
    geo_layer = create_map_layer(
        geodataframe=trajectories_colored,
        layer_style=PolylineLayerStyle(get_width=20, color_column="colors"),
        legend=LegendDefinition(label_column="speed_bins", color_column="colors"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layers=[TileLayer("OpenStreetMap")],
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_with_legend_multiple_layers(relocations, trajectories_colored):
    relocations["labels"] = relocations["fixtime"].apply(
        lambda x: "new" if x > relocations["fixtime"].median() else "old"
    )
    relocations["colors"] = relocations["fixtime"].apply(
        lambda x: (255, 0, 0, 255)
        if x > relocations["fixtime"].median()
        else (0, 0, 255, 255)
    )
    layer1 = create_map_layer(
        geodataframe=relocations,
        layer_style=PointLayerStyle(get_radius=15, fill_color_column="colors"),
        legend=LegendDefinition(label_column="labels", color_column="colors"),
    )
    layer2 = create_map_layer(
        geodataframe=trajectories_colored,
        layer_style=PolylineLayerStyle(get_width=20, color_column="colors"),
        legend=LegendDefinition(label_column="speed_bins", color_column="colors"),
    )

    map_html = draw_ecomap(
        geo_layers=[layer1, layer2],
        tile_layers=[TileLayer("OpenStreetMap")],
    )
    assert isinstance(map_html, str)


def test_draw_ecomap_widget_styles(trajectories_colored):
    geo_layer = create_map_layer(
        geodataframe=trajectories_colored,
        layer_style=PolylineLayerStyle(get_width=20, color_column="colors"),
        legend=LegendDefinition(label_column="speed_bins", color_column="colors"),
    )

    map_html = draw_ecomap(
        geo_layers=[geo_layer],
        tile_layers=[TileLayer("OpenStreetMap")],
        title="Test",
        north_arrow_style=NorthArrowStyle(placement="top-left"),
        legend_style=LegendStyle(placement="top-right"),
    )
    assert isinstance(map_html, str)
