import geopandas as gpd
from ecoscope_workflows.tasks.analysis import create_meshgrid
from random_geometry import random_3857_rectangle


def test_create_meshgrid():
    bounds = random_3857_rectangle(500, 500, 500, 500, utm_safe=True)
    aoi = gpd.GeoDataFrame(geometry=[bounds], crs="EPSG:3857")
    aoi = aoi.to_crs(4326)

    kws = dict(
        cell_width=100,
        cell_height=100,
    )
    meshgrid = create_meshgrid(aoi, **kws)

    assert len(meshgrid) > 0
    for point in aoi["geometry"]:
        assert meshgrid.intersects(point).any()
