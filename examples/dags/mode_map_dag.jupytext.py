# ruff: noqa: E402

# %% [markdown]
# # Map Example
# TODO: top level description

# %% [markdown]
# ## Imports

from functools import partial
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text

# %% [markdown]
# ## Get Subjectgroup Observations

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
# ## Get Subjectgroup Observations

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
# ## Get Subjectgroup Observations

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
# ## Draw Ecomap

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

ecomaps_partial = partial(draw_ecomap, **ecomaps_params)
ecomaps_mapped_iterable = map(ecomaps_partial, [obs_a, obs_b, obs_c])
ecomaps = list(ecomaps_mapped_iterable)


# %% [markdown]
# ## Persist Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    root_path=...,
    filename=...,
)

# %%
# call the task

td_ecomap_html_url_partial = partial(persist_text, **td_ecomap_html_url_params)
td_ecomap_html_url_mapped_iterable = map(td_ecomap_html_url_partial, ecomaps)
td_ecomap_html_url = list(td_ecomap_html_url_mapped_iterable)
