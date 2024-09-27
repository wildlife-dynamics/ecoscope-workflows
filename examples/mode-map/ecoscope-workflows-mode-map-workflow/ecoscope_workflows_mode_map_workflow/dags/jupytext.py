# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "6bfd073f8927e0208b78304117b118d3cdaec61dee5ccc830a3794426d697f0f"


# ruff: noqa: E402

# %% [markdown]
# # Mode Map
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text

# %% [markdown]
# ## Get Observations A

# %%
# parameters

obs_a_params = dict(
    client=...,
    subject_group_name=...,
    since=...,
    until=...,
    include_inactive=...,
)

# %%
# call the task


obs_a = get_subjectgroup_observations.partial(**obs_a_params).call()


# %% [markdown]
# ## Get Observations B

# %%
# parameters

obs_b_params = dict(
    client=...,
    subject_group_name=...,
    since=...,
    until=...,
    include_inactive=...,
)

# %%
# call the task


obs_b = get_subjectgroup_observations.partial(**obs_b_params).call()


# %% [markdown]
# ## Get Observations C

# %%
# parameters

obs_c_params = dict(
    client=...,
    subject_group_name=...,
    since=...,
    until=...,
    include_inactive=...,
)

# %%
# call the task


obs_c = get_subjectgroup_observations.partial(**obs_c_params).call()


# %% [markdown]
# ## Create Map Layer For Each Group

# %%
# parameters

map_layers_params = dict(
    layer_style=...,
    legend=...,
)

# %%
# call the task


map_layers = create_map_layer.partial(**map_layers_params).map(
    argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c]
)


# %% [markdown]
# ## Create EcoMap For Each Group

# %%
# parameters

ecomaps_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
    legend_style=...,
)

# %%
# call the task


ecomaps = draw_ecomap.partial(**ecomaps_params).map(
    argnames=["geo_layers"], argvalues=map_layers
)


# %% [markdown]
# ## Persist Ecomaps as Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task


td_ecomap_html_url = persist_text.partial(
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"], **td_ecomap_html_url_params
).map(argnames=["text"], argvalues=ecomaps)
