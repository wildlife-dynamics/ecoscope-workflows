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

# %% [markdown]
# ## Get Patrol Observations

# %%
# parameters

get_patrol_observations_params = dict(
    client=...,
    since=...,
    until=...,
    patrol_type=...,
    status=...,
    include_patrol_details=...,
)

# %%
# call the task

get_patrol_observations_return = get_patrol_observations(
    **get_patrol_observations_params,
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
    observations=get_patrol_observations_return,
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
    geodataframe=relocations_to_trajectory_return,
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
