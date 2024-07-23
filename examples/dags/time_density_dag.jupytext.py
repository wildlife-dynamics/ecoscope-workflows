# ruff: noqa: E402

# %% [markdown]
# # Calculate Time Density
# TODO: top level description

# %% [markdown]
# ## Imports

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view

# %% [markdown]
# ## Get Subjectgroup Observations

# %%
# parameters

get_subjectgroup_observations_params = dict(
    client=...,
    subject_group_name=...,
    include_inactive=...,
    since=...,
    until=...,
)

# %%
# call the task

get_subjectgroup_observations_return = get_subjectgroup_observations(
    **get_subjectgroup_observations_params,
)

# %% [markdown]
# ## Process Relocations

# %%
# parameters

process_relocations_params = dict(
    filter_point_coords=...,
    relocs_columns=...,
)

# %%
# call the task

process_relocations_return = process_relocations(
    observations=get_subjectgroup_observations_return,
    **process_relocations_params,
)
# %% [markdown]
# ## Relocations To Trajectory

# %%
# parameters

relocations_to_trajectory_params = dict(
    min_length_meters=...,
    max_length_meters=...,
    max_time_secs=...,
    min_time_secs=...,
    max_speed_kmhr=...,
    min_speed_kmhr=...,
)

# %%
# call the task

relocations_to_trajectory_return = relocations_to_trajectory(
    relocations=process_relocations_return,
    **relocations_to_trajectory_params,
)
# %% [markdown]
# ## Calculate Time Density

# %%
# parameters

calculate_time_density_params = dict(
    pixel_size=...,
    crs=...,
    nodata_value=...,
    band_count=...,
    max_speed_factor=...,
    expansion_factor=...,
    percentiles=...,
)

# %%
# call the task

calculate_time_density_return = calculate_time_density(
    trajectory_gdf=relocations_to_trajectory_return,
    **calculate_time_density_params,
)
# %% [markdown]
# ## Draw Ecomap

# %%
# parameters

draw_ecomap_params = dict(
    data_type=...,
    style_kws=...,
    tile_layer=...,
    static=...,
    title=...,
    title_kws=...,
    scale_kws=...,
    north_arrow_kws=...,
)

# %%
# call the task

draw_ecomap_return = draw_ecomap(
    geodataframe=calculate_time_density_return,
    **draw_ecomap_params,
)
# %% [markdown]
# ## Persist Text

# %%
# parameters

persist_text_params = dict(
    root_path=...,
    filename=...,
)

# %%
# call the task

persist_text_return = persist_text(
    text=draw_ecomap_return,
    **persist_text_params,
)
# %% [markdown]
# ## Create Map Widget Single View

# %%
# parameters

create_map_widget_single_view_params = dict(
    title=...,
    view=...,
)

# %%
# call the task

create_map_widget_single_view_return = create_map_widget_single_view(
    data=persist_text_return,
    **create_map_widget_single_view_params,
)
