import geopandas as gpd

from ecoscope_workflows.tasks.analysis import create_meshgrid
from shapely.geometry import Point


def test_create_meshgrid():
    algerian_rectangle = {
        "geometry": [
            Point(5.213756010299193, 26.356553143705952),
            Point(5.213756010299193, 24.88187588748029),
            Point(7.084885395692453, 24.88187588748029),
            Point(7.084885395692453, 26.356553143705952),
        ]
    }
    aoi = gpd.GeoDataFrame(algerian_rectangle, crs="EPSG:4326")

    kws = dict(
        cell_width=10000,
        cell_height=10000,
    )
    meshgrid = create_meshgrid(aoi, **kws)

    # at 1000x1000 we should divide AOI into four squares
    assert len(meshgrid) == 4
    for point in algerian_rectangle["geometry"]:
        assert meshgrid.intersects(point).any()
