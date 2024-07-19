# ruff: noqa: E402

# %% [markdown]
# # Calculate Time Density
# TODO: top level description

# %% [markdown]
# ## Get Subjectgroup Observations

# %%
# parameters

client = ...
subject_group_name = ...
include_inactive = ...
since = ...
until = ...


# %%
# the code for Get Subjectgroup Observations

"Get observations for a subject group from EarthRanger."

# %%
# return value from this section

get_subjectgroup_observations_return = client.get_subjectgroup_observations(
    subject_group_name=subject_group_name,
    include_subject_details=True,
    include_inactive=include_inactive,
    since=since,
    until=until,
)


# %% [markdown]
# ## Process Relocations
# %%
# dependencies assignments

observations = get_subjectgroup_observations_return


# %%
# parameters

filter_point_coords = ...
relocs_columns = ...


# %%
# the code for Process Relocations

from ecoscope.base import RelocsCoordinateFilter, Relocations

relocs = Relocations(observations)
relocs.apply_reloc_filter(
    RelocsCoordinateFilter(filter_point_coords=filter_point_coords), inplace=True
)
relocs.remove_filtered(inplace=True)
relocs = relocs[relocs_columns]
relocs.columns = [i.replace("extra__", "") for i in relocs.columns]
relocs.columns = [i.replace("subject__", "") for i in relocs.columns]

# %%
# return value from this section

process_relocations_return = relocs


# %% [markdown]
# ## Relocations To Trajectory
# %%
# dependencies assignments

relocations = process_relocations_return


# %%
# parameters

min_length_meters = ...
max_length_meters = ...
max_time_secs = ...
min_time_secs = ...
max_speed_kmhr = ...
min_speed_kmhr = ...


# %%
# the code for Relocations To Trajectory

from ecoscope.base import Relocations
from ecoscope.base import Trajectory, TrajSegFilter

traj = Trajectory.from_relocations(Relocations(relocations))
traj_seg_filter = TrajSegFilter(
    min_length_meters=min_length_meters,
    max_length_meters=max_length_meters,
    min_time_secs=min_time_secs,
    max_time_secs=max_time_secs,
    min_speed_kmhr=min_speed_kmhr,
    max_speed_kmhr=max_speed_kmhr,
)
traj.apply_traj_filter(traj_seg_filter, inplace=True)
traj.remove_filtered(inplace=True)

# %%
# return value from this section

relocations_to_trajectory_return = traj


# %% [markdown]
# ## Calculate Time Density
# %%
# dependencies assignments

trajectory_gdf = relocations_to_trajectory_return


# %%
# parameters

pixel_size = ...
crs = ...
nodata_value = ...
band_count = ...
max_speed_factor = ...
expansion_factor = ...
percentiles = ...


# %%
# the code for Calculate Time Density

import tempfile
from ecoscope.analysis.percentile import get_percentile_area
from ecoscope.analysis.UD import calculate_etd_range
from ecoscope.io.raster import RasterProfile

raster_profile = RasterProfile(
    pixel_size=pixel_size, crs=crs, nodata_value=nodata_value, band_count=band_count
)
trajectory_gdf.sort_values("segment_start", inplace=True)
tmp_tif_path = tempfile.NamedTemporaryFile(suffix=".tif")
calculate_etd_range(
    trajectory_gdf=trajectory_gdf,
    output_path=tmp_tif_path,
    max_speed_kmhr=max_speed_factor * trajectory_gdf["speed_kmhr"].max(),
    raster_profile=raster_profile,
    expansion_factor=expansion_factor,
)
result = get_percentile_area(percentile_levels=percentiles, raster_path=tmp_tif_path)
result.drop(columns="subject_id", inplace=True)
result["area_sqkm"] = result.area / 1000000.0

# %%
# return value from this section

calculate_time_density_return = result


# %% [markdown]
# ## Draw Ecomap
# %%
# dependencies assignments

geodataframe = calculate_time_density_return


# %%
# parameters

data_type = ...
style_kws = ...
tile_layer = ...
static = ...
title = ...
title_kws = ...
scale_kws = ...
north_arrow_kws = ...
output_path = ...


# %%
# the code for Draw Ecomap

'\n    Creates a map based on the provided layer definitions and configuration.\n\n    Args:\n    geodataframe (geopandas.GeoDataFrame): The geodataframe to visualize.\n    data_type (str): The type of visualization, "Scatterplot", "Path" or "Polygon".\n    style_kws (dict): Style arguments for the data visualization.\n    tile_layer (str): A named tile layer, ie OpenStreetMap.\n    static (bool): Set to true to disable map pan/zoom.\n    title (str): The map title.\n    title_kws (dict): Additional arguments for configuring the Title.\n    scale_kws (dict): Additional arguments for configuring the Scale Bar.\n    north_arrow_kws (dict): Additional arguments for configuring the North Arrow.\n\n    Returns:\n    str: A static HTML representation of the map.\n    '
from ecoscope.mapping import EcoMap

m = EcoMap(static=static, default_widgets=False)
if title:
    m.add_title(title, **title_kws)
m.add_scale_bar(**scale_kws)
m.add_north_arrow(**north_arrow_kws)
if tile_layer:
    m.add_layer(EcoMap.get_named_tile_layer(tile_layer))
match data_type:
    case "Scatterplot":
        m.add_scatterplot_layer(geodataframe, **style_kws)
    case "Path":
        m.add_path_layer(geodataframe, **style_kws)
    case "Polygon":
        m.add_polygon_layer(geodataframe, **style_kws)
m.zoom_to_bounds(m.layers)
return_result = output_path
if output_path:
    m.to_html(output_path)
else:
    return_result = m.to_html()

# %%
# return value from this section

draw_ecomap_return = return_result
