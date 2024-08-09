# ruff: noqa: E402

# %% [markdown]
# # Patrol Workflow
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.transformation import add_temporal_index
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter
from ecoscope_workflows.tasks.groupby import groupbykey
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views
from ecoscope_workflows.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows.tasks.results import create_plot_widget_single_view
from ecoscope_workflows.tasks.results import draw_pie_chart
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import gather_dashboard

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
# ## Get Patrol Observations from EarthRanger

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


patrol_obs = get_patrol_observations.call(**patrol_obs_params)


# %% [markdown]
# ## Transform Observations to Relocations

# %%
# parameters

patrol_reloc_params = dict(
    filter_point_coords=...,
    relocs_columns=...,
)

# %%
# call the task


patrol_reloc = process_relocations.partial(observations=patrol_obs).call(
    **patrol_reloc_params
)


# %% [markdown]
# ## Transform Relocations to Trajectories

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


patrol_traj = relocations_to_trajectory.partial(relocations=patrol_reloc).call(
    **patrol_traj_params
)


# %% [markdown]
# ## Add temporal index to Patrol Trajectories

# %%
# parameters

traj_add_temporal_index_params = dict(
    index_name=...,
    time_col=...,
    directive=...,
    cast_to_datetime=...,
    format=...,
)

# %%
# call the task


traj_add_temporal_index = add_temporal_index.partial(df=patrol_traj).call(
    **traj_add_temporal_index_params
)


# %% [markdown]
# ## Split Patrol Trajectories by Group

# %%
# parameters

split_patrol_traj_groups_params = dict()

# %%
# call the task


split_patrol_traj_groups = split_groups.partial(
    df=traj_add_temporal_index, groupers=groupers
).call(**split_patrol_traj_groups_params)


# %% [markdown]
# ## Create map layer for each Patrol Trajectories group

# %%
# parameters

patrol_traj_map_layers_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task


patrol_traj_map_layers = create_map_layer.partial(
    **patrol_traj_map_layers_params
).mapvalues(argnames=["geodataframe"], argvalues=split_patrol_traj_groups)


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
# ## Apply Relocation Coordinate Filter

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


filter_patrol_events = apply_reloc_coord_filter.partial(df=patrol_events).call(
    **filter_patrol_events_params
)


# %% [markdown]
# ## Add temporal index to Patrol Events

# %%
# parameters

pe_add_temporal_index_params = dict(
    index_name=...,
    time_col=...,
    directive=...,
    cast_to_datetime=...,
    format=...,
)

# %%
# call the task


pe_add_temporal_index = add_temporal_index.partial(df=filter_patrol_events).call(
    **pe_add_temporal_index_params
)


# %% [markdown]
# ## Split Patrol Events by Group

# %%
# parameters

split_pe_groups_params = dict()

# %%
# call the task


split_pe_groups = split_groups.partial(
    df=pe_add_temporal_index, groupers=groupers
).call(**split_pe_groups_params)


# %% [markdown]
# ## Create map layers for each Patrols Events group

# %%
# parameters

patrol_events_map_layers_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task


patrol_events_map_layers = create_map_layer.partial(
    **patrol_events_map_layers_params
).mapvalues(argnames=["geodataframe"], argvalues=split_pe_groups)


# %% [markdown]
# ## Combine Trajectories and Patrol Events layers

# %%
# parameters

combined_traj_and_pe_map_layers_params = dict()

# %%
# call the task


combined_traj_and_pe_map_layers = groupbykey.partial(
    iterables=[patrol_traj_map_layers, patrol_events_map_layers]
).call(**combined_traj_and_pe_map_layers_params)


# %% [markdown]
# ## Draw Ecomaps for each combined Trajectory and Patrol Events group

# %%
# parameters

traj_patrol_events_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    title_kws=...,
    scale_kws=...,
    north_arrow_kws=...,
)

# %%
# call the task


traj_patrol_events_ecomap = draw_ecomap.partial(
    **traj_patrol_events_ecomap_params
).mapvalues(argnames=["geo_layers"], argvalues=combined_traj_and_pe_map_layers)


# %% [markdown]
# ## Persist Patrols Ecomap as Text

# %%
# parameters

traj_pe_ecomap_html_urls_params = dict(
    filename=...,
)

# %%
# call the task


traj_pe_ecomap_html_urls = persist_text.partial(
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **traj_pe_ecomap_html_urls_params,
).mapvalues(argnames=["text"], argvalues=traj_patrol_events_ecomap)


# %% [markdown]
# ## Create Map Widgets for Patrol Events

# %%
# parameters

traj_pe_map_widgets_single_views_params = dict(
    title=...,
)

# %%
# call the task


traj_pe_map_widgets_single_views = create_map_widget_single_view.partial(
    **traj_pe_map_widgets_single_views_params
).map(argnames=["view", "data"], argvalues=traj_pe_ecomap_html_urls)


# %% [markdown]
# ## Merge EcoMap Widget Views

# %%
# parameters

traj_pe_grouped_map_widget_params = dict()

# %%
# call the task


traj_pe_grouped_map_widget = merge_widget_views.partial(
    widgets=traj_pe_map_widgets_single_views
).call(**traj_pe_grouped_map_widget_params)


# %% [markdown]
# ## Draw Time Series Bar Chart for Patrols Events

# %%
# parameters

patrol_events_bar_chart_params = dict(
    x_axis=...,
    y_axis=...,
    category=...,
    agg_function=...,
    time_interval=...,
    groupby_style_kws=...,
    style_kws=...,
    layout_kws=...,
)

# %%
# call the task


patrol_events_bar_chart = draw_time_series_bar_chart.partial(
    dataframe=filter_patrol_events
).call(**patrol_events_bar_chart_params)


# %% [markdown]
# ## Persist Patrols Bar Chart as Text

# %%
# parameters

patrol_events_bar_chart_html_url_params = dict(
    filename=...,
)

# %%
# call the task


patrol_events_bar_chart_html_url = persist_text.partial(
    text=patrol_events_bar_chart, root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"]
).call(**patrol_events_bar_chart_html_url_params)


# %% [markdown]
# ## Create Plot Widget for Patrol Events

# %%
# parameters

patrol_events_bar_chart_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


patrol_events_bar_chart_widget = create_plot_widget_single_view.partial(
    data=patrol_events_bar_chart_html_url
).call(**patrol_events_bar_chart_widget_params)


# %% [markdown]
# ## Draw Pie Chart for Patrols Events

# %%
# parameters

patrol_events_pie_chart_params = dict(
    value_column=...,
    label_column=...,
    style_kws=...,
    layout_kws=...,
)

# %%
# call the task


patrol_events_pie_chart = draw_pie_chart.partial(dataframe=filter_patrol_events).call(
    **patrol_events_pie_chart_params
)


# %% [markdown]
# ## Persist Patrols Pie Chart as Text

# %%
# parameters

patrol_events_pie_chart_html_url_params = dict(
    filename=...,
)

# %%
# call the task


patrol_events_pie_chart_html_url = persist_text.partial(
    text=patrol_events_pie_chart, root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"]
).call(**patrol_events_pie_chart_html_url_params)


# %% [markdown]
# ## Create Plot Widget for Patrol Events

# %%
# parameters

patrol_events_pie_chart_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


patrol_events_pie_chart_widget = create_plot_widget_single_view.partial(
    data=patrol_events_pie_chart_html_url
).call(**patrol_events_pie_chart_widget_params)


# %% [markdown]
# ## Calculate Time Density from Trajectory

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


td = calculate_time_density.partial(trajectory_gdf=patrol_traj).call(**td_params)


# %% [markdown]
# ## Create map layer from Time Density

# %%
# parameters

td_map_layer_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task


td_map_layer = create_map_layer.partial(geodataframe=td).call(**td_map_layer_params)


# %% [markdown]
# ## Draw Ecomap from Time Density

# %%
# parameters

td_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    title_kws=...,
    scale_kws=...,
    north_arrow_kws=...,
)

# %%
# call the task


td_ecomap = draw_ecomap.partial(geo_layers=td_map_layer).call(**td_ecomap_params)


# %% [markdown]
# ## Persist Ecomap as Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task


td_ecomap_html_url = persist_text.partial(
    text=td_ecomap, root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"]
).call(**td_ecomap_html_url_params)


# %% [markdown]
# ## Create Time Density Map Widget

# %%
# parameters

td_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


td_map_widget = create_map_widget_single_view.partial(data=td_ecomap_html_url).call(
    **td_map_widget_params
)


# %% [markdown]
# ## Create Dashboard with Patrol Map Widgets

# %%
# parameters

patrol_dashboard_params = dict(
    title=...,
    description=...,
)

# %%
# call the task


patrol_dashboard = gather_dashboard.partial(
    widgets=[
        traj_pe_grouped_map_widget,
        td_map_widget,
        patrol_events_bar_chart_widget,
        patrol_events_pie_chart_widget,
    ],
    groupers=groupers,
).call(**patrol_dashboard_params)
