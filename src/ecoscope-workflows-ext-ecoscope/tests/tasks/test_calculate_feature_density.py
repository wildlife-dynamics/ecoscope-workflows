import geopandas as gpd  # type: ignore[import-untyped]

from ecoscope_workflows_ext_ecoscope.tasks.analysis import (
    calculate_feature_density,
    create_meshgrid,
)
from ..utils.random_geometry import random_3857_rectangle, random_points_in_bounds


def test_calculate_feature_density():
    bounds = random_3857_rectangle(500, 500, 500, 500, utm_safe=True)

    aoi = gpd.GeoDataFrame(geometry=[bounds], crs="EPSG:3857")
    meshgrid = create_meshgrid(aoi, cell_width=100, cell_height=100)
    random_points = random_points_in_bounds(bounds, 200)
    points_gdf = gpd.GeoDataFrame(geometry=random_points, crs="EPSG:3857")

    result = calculate_feature_density(
        geodataframe=points_gdf,
        meshgrid=meshgrid,
        geometry_type="point",
    )

    # the sum of all density vals should equal our number of points
    assert result.density.sum() == 200
