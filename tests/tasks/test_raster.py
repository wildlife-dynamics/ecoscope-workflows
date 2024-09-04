import random
import geopandas as gpd

from ecoscope_workflows.tasks.analysis import create_meshgrid
from ecoscope_workflows.tasks.results._raster import grid_to_raster
from random_geometry import random_3857_rectangle


def test_grid_to_raster():
    bounds = random_3857_rectangle(200000, 200000, 200000, 200000, utm_safe=True)
    aoi = gpd.GeoDataFrame(geometry=[bounds], crs="EPSG:3857")

    cell_width = 10000
    cell_height = 10000

    grid = create_meshgrid(
        aoi, cell_width=cell_width, cell_height=cell_height, intersecting_only=False
    )
    grid["fake_density"] = grid.apply(lambda _: random.randint(1, 50), axis=1)

    raster = grid_to_raster(grid, value_column="fake_density")
    assert raster is not None
