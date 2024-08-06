# ruff: noqa: E402

# %% [markdown]
# # Map Example
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
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


obs_a = get_subjectgroup_observations.call(**obs_a_params)


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


obs_b = get_subjectgroup_observations.call(**obs_b_params)


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


obs_c = get_subjectgroup_observations.call(**obs_c_params)


# %% [markdown]
# ## Creat EcoMap For Each Group

# %%
# parameters

ecomaps_params = dict(
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


ecomaps = draw_ecomap.map(argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c])


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
