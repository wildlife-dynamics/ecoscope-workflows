# ruff: noqa: E402

# %% [markdown]
# # Map Example
# TODO: top level description

# %% [markdown]
# ## Imports

from functools import partial
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.parallel import split_groups
from ecoscope_workflows.tasks.results import draw_ecomap

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
# ## Split Groups

# %%
# parameters

split_params = dict()

# %%
# call the task

split = split_groups(
    df=obs,
    **split_params,
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
ecomaps_mapped_iterable = map(ecomaps_partial, split)
ecomaps = list(ecomaps_mapped_iterable)
