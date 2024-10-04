# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "748252e8fb420e7edc39e0b05c8793c569ddb0fed5f92830889f0dcebdb72be1"


# ruff: noqa: E402

# %% [markdown]
# # Patrols
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_ext_ecoscope.tasks.io import get_patrol_observations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import process_relocations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import (
    relocations_to_trajectory,
)
from ecoscope_workflows_core.tasks.transformation import add_temporal_index
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.io import get_patrol_events
from ecoscope_workflows_ext_ecoscope.tasks.transformation import (
    apply_reloc_coord_filter,
)
from ecoscope_workflows_core.tasks.groupby import groupbykey
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.analysis import dataframe_column_nunique
from ecoscope_workflows_core.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows_core.tasks.analysis import dataframe_column_sum
from ecoscope_workflows_core.tasks.transformation import with_unit
from ecoscope_workflows_core.tasks.analysis import dataframe_column_mean
from ecoscope_workflows_core.tasks.analysis import dataframe_column_max
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows_core.tasks.results import create_plot_widget_single_view
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_pie_chart
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_time_density
from ecoscope_workflows_core.tasks.results import gather_dashboard

# %% [markdown]
# ## Set Groupers

# %%
# parameters

groupers_params = dict(
    groupers=...,
)

# %%
# call the task


groupers = set_groupers.partial(**groupers_params).call()


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


patrol_obs = get_patrol_observations.partial(**patrol_obs_params).call()


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


patrol_reloc = process_relocations.partial(
    observations=patrol_obs, **patrol_reloc_params
).call()


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


patrol_traj = relocations_to_trajectory.partial(
    relocations=patrol_reloc, **patrol_traj_params
).call()


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


traj_add_temporal_index = add_temporal_index.partial(
    df=patrol_traj, **traj_add_temporal_index_params
).call()


# %% [markdown]
# ## Split Patrol Trajectories by Group

# %%
# parameters

split_patrol_traj_groups_params = dict()

# %%
# call the task


split_patrol_traj_groups = split_groups.partial(
    df=traj_add_temporal_index, groupers=groupers, **split_patrol_traj_groups_params
).call()


# %% [markdown]
# ## Create map layer for each Patrol Trajectories group

# %%
# parameters

patrol_traj_map_layers_params = dict(
    layer_style=...,
    legend=...,
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


patrol_events = get_patrol_events.partial(**patrol_events_params).call()


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


filter_patrol_events = apply_reloc_coord_filter.partial(
    df=patrol_events, **filter_patrol_events_params
).call()


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


pe_add_temporal_index = add_temporal_index.partial(
    df=filter_patrol_events, **pe_add_temporal_index_params
).call()


# %% [markdown]
# ## Split Patrol Events by Group

# %%
# parameters

split_pe_groups_params = dict()

# %%
# call the task


split_pe_groups = split_groups.partial(
    df=pe_add_temporal_index, groupers=groupers, **split_pe_groups_params
).call()


# %% [markdown]
# ## Create map layers for each Patrols Events group

# %%
# parameters

patrol_events_map_layers_params = dict(
    layer_style=...,
    legend=...,
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
    iterables=[patrol_traj_map_layers, patrol_events_map_layers],
    **combined_traj_and_pe_map_layers_params,
).call()


# %% [markdown]
# ## Draw Ecomaps for each combined Trajectory and Patrol Events group

# %%
# parameters

traj_patrol_events_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
    legend_style=...,
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
    widgets=traj_pe_map_widgets_single_views, **traj_pe_grouped_map_widget_params
).call()


# %% [markdown]
# ## Calculate Total Patrols Per Group

# %%
# parameters

total_patrols_params = dict(
    column_name=...,
)

# %%
# call the task


total_patrols = dataframe_column_nunique.partial(**total_patrols_params).mapvalues(
    argnames=["df"], argvalues=split_patrol_traj_groups
)


# %% [markdown]
# ## Create Single Value Widgets for Total Patrols Per Group

# %%
# parameters

total_patrols_sv_widgets_params = dict(
    title=...,
    decimal_places=...,
)

# %%
# call the task


total_patrols_sv_widgets = create_single_value_widget_single_view.partial(
    **total_patrols_sv_widgets_params
).map(argnames=["view", "data"], argvalues=total_patrols)


# %% [markdown]
# ## Merge per group Total Patrols SV widgets

# %%
# parameters

total_patrols_grouped_sv_widget_params = dict()

# %%
# call the task


total_patrols_grouped_sv_widget = merge_widget_views.partial(
    widgets=total_patrols_sv_widgets, **total_patrols_grouped_sv_widget_params
).call()


# %% [markdown]
# ## Calculate Total Patrol Time Per Group

# %%
# parameters

total_patrol_time_params = dict(
    column_name=...,
)

# %%
# call the task


total_patrol_time = dataframe_column_sum.partial(**total_patrol_time_params).mapvalues(
    argnames=["df"], argvalues=split_patrol_traj_groups
)


# %% [markdown]
# ## Convert total patrol time units

# %%
# parameters

total_patrol_time_converted_params = dict(
    original_unit=...,
    new_unit=...,
)

# %%
# call the task


total_patrol_time_converted = with_unit.partial(
    **total_patrol_time_converted_params
).mapvalues(argnames=["value"], argvalues=total_patrol_time)


# %% [markdown]
# ## Create Single Value Widgets for Total Patrol Time Per Group

# %%
# parameters

total_patrol_time_sv_widgets_params = dict(
    title=...,
    decimal_places=...,
)

# %%
# call the task


total_patrol_time_sv_widgets = create_single_value_widget_single_view.partial(
    **total_patrol_time_sv_widgets_params
).map(argnames=["view", "data"], argvalues=total_patrol_time_converted)


# %% [markdown]
# ## Merge per group Total Patrol Time SV widgets

# %%
# parameters

patrol_time_grouped_widget_params = dict()

# %%
# call the task


patrol_time_grouped_widget = merge_widget_views.partial(
    widgets=total_patrol_time_sv_widgets, **patrol_time_grouped_widget_params
).call()


# %% [markdown]
# ## Calculate Total Distance Per Group

# %%
# parameters

total_patrol_dist_params = dict(
    column_name=...,
)

# %%
# call the task


total_patrol_dist = dataframe_column_sum.partial(**total_patrol_dist_params).mapvalues(
    argnames=["df"], argvalues=split_patrol_traj_groups
)


# %% [markdown]
# ## Convert total patrol distance units

# %%
# parameters

total_patrol_dist_converted_params = dict(
    original_unit=...,
    new_unit=...,
)

# %%
# call the task


total_patrol_dist_converted = with_unit.partial(
    **total_patrol_dist_converted_params
).mapvalues(argnames=["value"], argvalues=total_patrol_dist)


# %% [markdown]
# ## Create Single Value Widgets for Total Distance Per Group

# %%
# parameters

total_patrol_dist_sv_widgets_params = dict(
    title=...,
    decimal_places=...,
)

# %%
# call the task


total_patrol_dist_sv_widgets = create_single_value_widget_single_view.partial(
    **total_patrol_dist_sv_widgets_params
).map(argnames=["view", "data"], argvalues=total_patrol_dist_converted)


# %% [markdown]
# ## Merge per group Total Patrol Distance SV widgets

# %%
# parameters

patrol_dist_grouped_widget_params = dict()

# %%
# call the task


patrol_dist_grouped_widget = merge_widget_views.partial(
    widgets=total_patrol_dist_sv_widgets, **patrol_dist_grouped_widget_params
).call()


# %% [markdown]
# ## Calculate Average Speed Per Group

# %%
# parameters

avg_speed_params = dict(
    column_name=...,
)

# %%
# call the task


avg_speed = dataframe_column_mean.partial(**avg_speed_params).mapvalues(
    argnames=["df"], argvalues=split_patrol_traj_groups
)


# %% [markdown]
# ## Convert Average Speed units

# %%
# parameters

average_speed_converted_params = dict(
    original_unit=...,
    new_unit=...,
)

# %%
# call the task


average_speed_converted = with_unit.partial(**average_speed_converted_params).mapvalues(
    argnames=["value"], argvalues=avg_speed
)


# %% [markdown]
# ## Create Single Value Widgets for Avg Speed Per Group

# %%
# parameters

avg_speed_sv_widgets_params = dict(
    title=...,
    decimal_places=...,
)

# %%
# call the task


avg_speed_sv_widgets = create_single_value_widget_single_view.partial(
    **avg_speed_sv_widgets_params
).map(argnames=["view", "data"], argvalues=average_speed_converted)


# %% [markdown]
# ## Merge per group Avg Speed SV widgets

# %%
# parameters

avg_speed_grouped_widget_params = dict()

# %%
# call the task


avg_speed_grouped_widget = merge_widget_views.partial(
    widgets=avg_speed_sv_widgets, **avg_speed_grouped_widget_params
).call()


# %% [markdown]
# ## Calculate Max Speed Per Group

# %%
# parameters

max_speed_params = dict(
    column_name=...,
)

# %%
# call the task


max_speed = dataframe_column_max.partial(**max_speed_params).mapvalues(
    argnames=["df"], argvalues=split_patrol_traj_groups
)


# %% [markdown]
# ## Convert Max Speed units

# %%
# parameters

max_speed_converted_params = dict(
    original_unit=...,
    new_unit=...,
)

# %%
# call the task


max_speed_converted = with_unit.partial(**max_speed_converted_params).mapvalues(
    argnames=["value"], argvalues=max_speed
)


# %% [markdown]
# ## Create Single Value Widgets for Max Speed Per Group

# %%
# parameters

max_speed_sv_widgets_params = dict(
    title=...,
    decimal_places=...,
)

# %%
# call the task


max_speed_sv_widgets = create_single_value_widget_single_view.partial(
    **max_speed_sv_widgets_params
).map(argnames=["view", "data"], argvalues=max_speed_converted)


# %% [markdown]
# ## Merge per group Max Speed SV widgets

# %%
# parameters

max_speed_grouped_widget_params = dict()

# %%
# call the task


max_speed_grouped_widget = merge_widget_views.partial(
    widgets=max_speed_sv_widgets, **max_speed_grouped_widget_params
).call()


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
    color_column=...,
    grouped_styles=...,
    plot_style=...,
    layout_style=...,
)

# %%
# call the task


patrol_events_bar_chart = draw_time_series_bar_chart.partial(
    dataframe=filter_patrol_events, **patrol_events_bar_chart_params
).call()


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
    text=patrol_events_bar_chart,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **patrol_events_bar_chart_html_url_params,
).call()


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
    data=patrol_events_bar_chart_html_url, **patrol_events_bar_chart_widget_params
).call()


# %% [markdown]
# ## Draw Pie Chart for Patrols Events

# %%
# parameters

patrol_events_pie_chart_params = dict(
    value_column=...,
    label_column=...,
    color_column=...,
    plot_style=...,
    layout_style=...,
)

# %%
# call the task


patrol_events_pie_chart = draw_pie_chart.partial(
    **patrol_events_pie_chart_params
).mapvalues(argnames=["dataframe"], argvalues=split_pe_groups)


# %% [markdown]
# ## Persist Patrols Pie Chart as Text

# %%
# parameters

pe_pie_chart_html_urls_params = dict(
    filename=...,
)

# %%
# call the task


pe_pie_chart_html_urls = persist_text.partial(
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"], **pe_pie_chart_html_urls_params
).mapvalues(argnames=["text"], argvalues=patrol_events_pie_chart)


# %% [markdown]
# ## Create Plot Widget for Patrol Events

# %%
# parameters

patrol_events_pie_chart_widgets_params = dict(
    title=...,
)

# %%
# call the task


patrol_events_pie_chart_widgets = create_plot_widget_single_view.partial(
    **patrol_events_pie_chart_widgets_params
).map(argnames=["view", "data"], argvalues=pe_pie_chart_html_urls)


# %% [markdown]
# ## Merge Pie Chart Widget Views

# %%
# parameters

patrol_events_pie_widget_grouped_params = dict()

# %%
# call the task


patrol_events_pie_widget_grouped = merge_widget_views.partial(
    widgets=patrol_events_pie_chart_widgets, **patrol_events_pie_widget_grouped_params
).call()


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


td = calculate_time_density.partial(trajectory_gdf=patrol_traj, **td_params).call()


# %% [markdown]
# ## Create map layer from Time Density

# %%
# parameters

td_map_layer_params = dict(
    layer_style=...,
    legend=...,
)

# %%
# call the task


td_map_layer = create_map_layer.partial(geodataframe=td, **td_map_layer_params).call()


# %% [markdown]
# ## Draw Ecomap from Time Density

# %%
# parameters

td_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
    legend_style=...,
)

# %%
# call the task


td_ecomap = draw_ecomap.partial(geo_layers=td_map_layer, **td_ecomap_params).call()


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
    text=td_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **td_ecomap_html_url_params,
).call()


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


td_map_widget = create_map_widget_single_view.partial(
    data=td_ecomap_html_url, **td_map_widget_params
).call()


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
        patrol_events_pie_widget_grouped,
        total_patrols_grouped_sv_widget,
        patrol_time_grouped_widget,
        patrol_dist_grouped_widget,
        avg_speed_grouped_widget,
        max_speed_grouped_widget,
    ],
    groupers=groupers,
    **patrol_dashboard_params,
).call()
