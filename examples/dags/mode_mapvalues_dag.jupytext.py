# ruff: noqa: E402

# %% [markdown]
# # Mapvalues Example
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views
from ecoscope_workflows.tasks.results import gather_dashboard

# %% [markdown]
# ## Get Patrol Events from EarthRanger

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


patrol_events = get_patrol_events.call(**patrol_events_params)


# %% [markdown]
# ## Set Groupers

# %%
# parameters

groupers_params = dict(
    groupers=...,
)

# %%
# call the task


groupers = set_groupers.call(**groupers_params)


# %% [markdown]
# ## Split Observations

# %%
# parameters

split_obs_params = dict()

# %%
# call the task


split_obs = split_groups.partial(df=patrol_events, groupers=groupers).call(
    **split_obs_params
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


map_layers = create_map_layer.partial(**map_layers_params).mapvalues(
    argnames=["geodataframe"], argvalues=split_obs
)


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


ecomaps = draw_ecomap.partial(**ecomaps_params).mapvalues(
    argnames=["geo_layers"], argvalues=map_layers
)


# %% [markdown]
# ## Persist EcoMaps

# %%
# parameters

ecomaps_persist_params = dict(
    filename=...,
)

# %%
# call the task


ecomaps_persist = persist_text.partial(
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"], **ecomaps_persist_params
).mapvalues(argnames=["text"], argvalues=ecomaps)


# %% [markdown]
# ## Create EcoMap Widgets

# %%
# parameters

ecomap_widgets_params = dict(
    title=...,
)

# %%
# call the task


ecomap_widgets = create_map_widget_single_view.partial(**ecomap_widgets_params).map(
    argnames=["view", "data"], argvalues=ecomaps_persist
)


# %% [markdown]
# ## Merge EcoMap Widget Views

# %%
# parameters

ecomap_widgets_merged_params = dict()

# %%
# call the task


ecomap_widgets_merged = merge_widget_views.partial(widgets=ecomap_widgets).call(
    **ecomap_widgets_merged_params
)


# %% [markdown]
# ## Create EcoMap Dashboard

# %%
# parameters

dashboard_params = dict(
    title=...,
    description=...,
)

# %%
# call the task


dashboard = gather_dashboard.partial(
    widgets=ecomap_widgets_merged, groupers=groupers
).call(**dashboard_params)
