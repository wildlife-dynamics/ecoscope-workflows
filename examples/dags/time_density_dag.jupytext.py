# ruff: noqa: E402

# %% [markdown]
# # Calculate Time Density
# TODO: top level description

# %% [markdown]
# ## Get Subjectgroup Observations

# %%
# parameters

server = ...
username = ...
password = ...
tcp_limit = ...
sub_page_size = ...
subject_group_name = ...
include_inactive = ...
since = ...
until = ...


# %%
# the code for Get Subjectgroup Observations

from ecoscope.io import EarthRangerIO

earthranger_io = EarthRangerIO(
    server=server,
    username=username,
    password=password,
    tcp_limit=tcp_limit,
    sub_page_size=sub_page_size,
)

# %%
# return value from this section

get_subjectgroup_observations_return = earthranger_io.get_subjectgroup_observations(
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

static = ...
height = ...
width = ...
search_control = ...
title = ...
title_kws = ...
tile_layers = ...
north_arrow_kws = ...
add_gdf_kws = ...


# %%
# the code for Draw Ecomap

from ecoscope.mapping import EcoMap

m = EcoMap(static=static, height=height, width=width, search_control=search_control)
m.add_title(title=title, **title_kws)
for tl in tile_layers:
    m.add_tile_layer(**tl)
m.add_north_arrow(**north_arrow_kws)
m.add_gdf(geodataframe, **add_gdf_kws)
m.zoom_to_gdf(geodataframe)

# %%
# return value from this section

draw_ecomap_return = m._repr_html_(fill_parent=True)
