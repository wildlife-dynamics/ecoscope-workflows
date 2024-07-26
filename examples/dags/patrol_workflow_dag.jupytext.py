# ruff: noqa: E402

# %% [markdown]
# # Patrol Workflow
# TODO: top level description

# %% [markdown]
# ## Imports

from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import gather_dashboard
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter

# %% [markdown]
# ## Get Patrol Observations

# %%
# parameters

patrol_obs_params = dict(
    client=...,
    since=...,
    until=...,
    patrol_type=...,
    status=...,
    include_patrol_details=...,
)

# %%
# call the task

patrol_obs = get_patrol_observations(
    **patrol_obs_params,
)

# %% [markdown]
# ## Process Relocations

# %%
# parameters

patrol_reloc_params = dict(
    filter_point_coords=...,
    relocs_columns=...,
)

# %%
# call the task

patrol_reloc = process_relocations(
    observations=patrol_obs,
    **patrol_reloc_params,
)
# %% [markdown]
# ## Relocations To Trajectory

# %%
# parameters

patrol_traj_params = dict(
    min_length_meters=...,
    max_length_meters=...,
    max_time_secs=...,
    min_time_secs=...,
    max_speed_kmhr=...,
    min_speed_kmhr=...,
)

# %%
# call the task

patrol_traj = relocations_to_trajectory(
    relocations=patrol_reloc,
    **patrol_traj_params,
)
# %% [markdown]
# ## Draw Ecomap

# %%
# parameters

patrol_ecomap_params = dict(
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

patrol_ecomap = draw_ecomap(
    geodataframe=patrol_traj,
    **patrol_ecomap_params,
)
# %% [markdown]
# ## Persist Text

# %%
# parameters

patrol_ecomap_html_url_params = dict(
    root_path=...,
    filename=...,
)

# %%
# call the task

patrol_ecomap_html_url = persist_text(
    text=patrol_ecomap,
    **patrol_ecomap_html_url_params,
)
# %% [markdown]
# ## Create Map Widget Single View

# %%
# parameters

patrol_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task

patrol_map_widget = create_map_widget_single_view(
    data=patrol_ecomap_html_url,
    **patrol_map_widget_params,
)
# %% [markdown]
# ## Gather Dashboard

# %%
# parameters

patrol_dashboard_params = dict(
    title=...,
    description=...,
    groupers=...,
)

# %%
# call the task

patrol_dashboard = gather_dashboard(
    widgets=patrol_map_widget,
    **patrol_dashboard_params,
)
# %% [markdown]
# ## Get Patrol Events

# %%
# parameters

patrol_events_params = dict(
    client=...,
    since=...,
    until=...,
    patrol_type=...,
    status=...,
)

# %%
# call the task

patrol_events = get_patrol_events(
    **patrol_events_params,
)

# %% [markdown]
# ## Apply Reloc Coord Filter

# %%
# parameters

filter_patrol_events_params = dict(
    min_x=...,
    max_x=...,
    min_y=...,
    max_y=...,
    filter_point_coords=...,
)

# %%
# call the task

filter_patrol_events = apply_reloc_coord_filter(
    df=patrol_events,
    **filter_patrol_events_params,
)
