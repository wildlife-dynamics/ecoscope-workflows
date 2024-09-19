import geopandas as gpd  # type: ignore[import-untyped]

from ecoscope_workflows.ext.ecoscope.tasks.analysis import create_meshgrid
from ..utils.random_geometry import random_3857_rectangle


def test_create_meshgrid():
    bounds = random_3857_rectangle(500, 500, 500, 500, utm_safe=True)
    aoi = gpd.GeoDataFrame(geometry=[bounds], crs="EPSG:3857")

    meshgrid = create_meshgrid(aoi, cell_width=100, cell_height=100)

    assert len(meshgrid) > 0
    for point in aoi["geometry"]:
        assert meshgrid.intersects(point).any()
