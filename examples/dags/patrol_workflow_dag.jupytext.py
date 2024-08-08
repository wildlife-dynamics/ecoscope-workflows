# ruff: noqa: E402

# %% [markdown]
# # Patrol Workflow
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows.tasks.results import create_plot_widget_single_view
from ecoscope_workflows.tasks.results import draw_pie_chart
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import gather_dashboard

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
# ## Create map layer from Trajectories

# %%
# parameters

patrol_traj_map_layer_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task


patrol_traj_map_layer = create_map_layer.partial(geodataframe=patrol_traj).call(
    **patrol_traj_map_layer_params
)


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
# ## Create map layer from Patrols Events

# %%
# parameters

patrol_events_map_layer_params = dict(
    data_type=...,
    style_kws=...,
)

# %%
# call the task


patrol_events_map_layer = create_map_layer.partial(
    geodataframe=filter_patrol_events
).call(**patrol_events_map_layer_params)


# %% [markdown]
# ## Draw Ecomap for Trajectories and Patrol Events

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
    geo_layers=[patrol_traj_map_layer, patrol_events_map_layer]
).call(**traj_patrol_events_ecomap_params)


# %% [markdown]
# ## Persist Patrols Ecomap as Text

# %%
# parameters

traj_pe_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task


traj_pe_ecomap_html_url = persist_text.partial(
    text=traj_patrol_events_ecomap, root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"]
).call(**traj_pe_ecomap_html_url_params)


# %% [markdown]
# ## Create Map Widget for Patrol Events

# %%
# parameters

traj_patrol_events_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


traj_patrol_events_map_widget = create_map_widget_single_view.partial(
    data=traj_pe_ecomap_html_url
).call(**traj_patrol_events_map_widget_params)


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
    groupers=...,
)

# %%
# call the task


patrol_dashboard = gather_dashboard.partial(
    widgets=[
        traj_patrol_events_map_widget,
        td_map_widget,
        patrol_events_bar_chart_widget,
        patrol_events_pie_chart_widget,
    ]
).call(**patrol_dashboard_params)
