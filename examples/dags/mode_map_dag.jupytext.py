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
# ## Creat EcoMap For Each Group

# %%
# parameters

ecomaps_params = dict(
    data_type=...,
    style_kws=...,
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_property=...,
)

# %%
# call the task

ecomaps_mapped_iterable = map(
    lambda kw: draw_ecomap.replace(validate=True)(**kw),
    [
        {
            "geodataframe": i,
        }
        | ecomaps_params
        for i in [obs_a, obs_b, obs_c]
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
