# ruff: noqa: E402

# %% [markdown]
# # Map Example
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text

# %% [markdown]
# ## Get Observations A

# %%
# parameters

obs_a_params = dict(
    client=...,
    subject_group_name=...,
    include_inactive=...,
    since=...,
    until=...,
)

# %%
# call the task

obs_a = get_subjectgroup_observations(
    **obs_a_params,
)

# %% [markdown]
# ## Get Observations B

# %%
# parameters

obs_b_params = dict(
    client=...,
    subject_group_name=...,
    include_inactive=...,
    since=...,
    until=...,
)

# %%
# call the task

obs_b = get_subjectgroup_observations(
    **obs_b_params,
)

# %% [markdown]
# ## Get Observations C

# %%
# parameters

obs_c_params = dict(
    client=...,
    subject_group_name=...,
    include_inactive=...,
    since=...,
    until=...,
)

# %%
# call the task

obs_c = get_subjectgroup_observations(
    **obs_c_params,
)

# %% [markdown]
# ## Create Map Layer For Each Group

# %%
# parameters

map_layers_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task

map_layers_mapped_iterable = map(
    lambda kw: create_map_layer.replace(validate=True)(**kw),
    [
        {
            "geodataframe": i,
        }
        | map_layers_params
        for i in [obs_a, obs_b, obs_c]
    ],
)
map_layers = list(map_layers_mapped_iterable)


# %% [markdown]
# ## Create EcoMap For Each Group

# %%
# parameters

ecomaps_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    title_kws=...,
    scale_kws=...,
    north_arrow_kws=...,
)

# %%
# call the task

ecomaps_mapped_iterable = map(
    lambda kw: draw_ecomap.replace(validate=True)(**kw),
    [
        {
            "geo_layers": i,
        }
        | ecomaps_params
        for i in [map_layers]
    ],
)
ecomaps = list(ecomaps_mapped_iterable)


# %% [markdown]
# ## Persist Ecomaps as Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task

td_ecomap_html_url_mapped_iterable = map(
    lambda kw: persist_text.replace(validate=True)(**kw),
    [
        {
            "text": i,
            "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        }
        | td_ecomap_html_url_params
        for i in ecomaps
    ],
)
td_ecomap_html_url = list(td_ecomap_html_url_mapped_iterable)
