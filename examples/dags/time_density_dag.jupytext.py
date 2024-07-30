# ruff: noqa: E402

# %% [markdown]
# # Calculate Time Density
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import gather_dashboard

# %% [markdown]
# ## Get Subjectgroup Observations

# %%
# parameters

obs_params = dict(
    client=...,
    subject_group_name=...,
    include_inactive=...,
    since=...,
    until=...,
)

# %%
# call the task

obs = get_subjectgroup_observations(
    **obs_params,
)

# %% [markdown]
# ## Process Relocations

# %%
# parameters

reloc_params = dict(
    filter_point_coords=...,
    relocs_columns=...,
)

# %%
# call the task

reloc = process_relocations(
    observations=obs,
    **reloc_params,
)

# %% [markdown]
# ## Relocations To Trajectory

# %%
# parameters

traj_params = dict(
    min_length_meters=...,
    max_length_meters=...,
    max_time_secs=...,
    min_time_secs=...,
    max_speed_kmhr=...,
    min_speed_kmhr=...,
)

# %%
# call the task

traj = relocations_to_trajectory(
    relocations=reloc,
    **traj_params,
)

# %% [markdown]
# ## Calculate Time Density

# %%
# parameters

td_params = dict(
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

td = calculate_time_density(
    trajectory_gdf=traj,
    **td_params,
)

# %% [markdown]
# ## Draw Ecomap

# %%
# parameters

td_ecomap_params = dict(
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

td_ecomap = draw_ecomap(
    geodataframe=td,
    **td_ecomap_params,
)

# %% [markdown]
# ## Persist Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task

td_ecomap_html_url = persist_text(
    text=td_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **td_ecomap_html_url_params,
)

# %% [markdown]
# ## Create Map Widget Single View

# %%
# parameters

td_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task

td_map_widget = create_map_widget_single_view(
    data=td_ecomap_html_url,
    **td_map_widget_params,
)

# %% [markdown]
# ## Gather Dashboard

# %%
# parameters

td_dashboard_params = dict(
    title=...,
    description=...,
    groupers=...,
)

# %%
# call the task

td_dashboard = gather_dashboard(
    widgets=td_map_widget,
    **td_dashboard_params,
)
