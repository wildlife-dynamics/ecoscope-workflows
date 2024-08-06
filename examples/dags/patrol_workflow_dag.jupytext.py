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
from ecoscope_workflows.tasks.results import draw_stacked_bar_chart
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

patrol_obs = get_patrol_observations(
    **patrol_obs_params,
)

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

patrol_reloc = process_relocations(
    observations=patrol_obs,
    **patrol_reloc_params,
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

patrol_traj = relocations_to_trajectory(
    relocations=patrol_reloc,
    **patrol_traj_params,
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

patrol_traj_map_layer = create_map_layer(
    geodataframe=patrol_traj,
    **patrol_traj_map_layer_params,
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

patrol_events = get_patrol_events(
    **patrol_events_params,
)

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

filter_patrol_events = apply_reloc_coord_filter(
    df=patrol_events,
    **filter_patrol_events_params,
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

patrol_events_map_layer = create_map_layer(
    geodataframe=filter_patrol_events,
    **patrol_events_map_layer_params,
)

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

traj_patrol_events_ecomap = draw_ecomap(
    geo_layers=[patrol_traj_map_layer, patrol_events_map_layer],
    **traj_patrol_events_ecomap_params,
)

# %% [markdown]
# ## Persist Patrols Ecomap as Text

# %%
# parameters

traj_pe_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task

traj_pe_ecomap_html_url = persist_text(
    text=traj_patrol_events_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **traj_pe_ecomap_html_url_params,
)

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

traj_patrol_events_map_widget = create_map_widget_single_view(
    data=traj_pe_ecomap_html_url,
    **traj_patrol_events_map_widget_params,
)

# %% [markdown]
# ## Draw Stacked Bar Chart for Patrols Events

# %%
# parameters

patrol_events_bar_chart_params = dict(
    x_axis=...,
    y_axis=...,
    stack_column=...,
    agg_function=...,
    groupby_style_kws=...,
    style_kws=...,
    layout_kws=...,
)

# %%
# call the task

patrol_events_bar_chart = draw_stacked_bar_chart(
    dataframe=filter_patrol_events,
    **patrol_events_bar_chart_params,
)

# %% [markdown]
# ## Persist Patrols Bar Chart as Text

# %%
# parameters

patrol_events_bar_chart_html_url_params = dict(
    filename=...,
)

# %%
# call the task

patrol_events_bar_chart_html_url = persist_text(
    text=patrol_events_bar_chart,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **patrol_events_bar_chart_html_url_params,
)

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

patrol_events_bar_chart_widget = create_plot_widget_single_view(
    data=patrol_events_bar_chart_html_url,
    **patrol_events_bar_chart_widget_params,
)

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

patrol_events_pie_chart = draw_pie_chart(
    dataframe=filter_patrol_events,
    **patrol_events_pie_chart_params,
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

patrol_events_pie_chart_html_url = persist_text(
    text=patrol_events_pie_chart,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **patrol_events_pie_chart_html_url_params,
)

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

patrol_events_pie_chart_widget = create_plot_widget_single_view(
    data=patrol_events_pie_chart_html_url,
    **patrol_events_pie_chart_widget_params,
)

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

td = calculate_time_density(
    trajectory_gdf=patrol_traj,
    **td_params,
)

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

td_map_layer = create_map_layer(
    geodataframe=td,
    **td_map_layer_params,
)

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

td_ecomap = draw_ecomap(
    geo_layers=[td_map_layer],
    **td_ecomap_params,
)

# %% [markdown]
# ## Persist Ecomap as Text

# %%
# parameters

td_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task

td_ecomap_html_url = persist_text(
    text=td_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **td_ecomap_html_url_params,
)

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

td_map_widget = create_map_widget_single_view(
    data=td_ecomap_html_url,
    **td_map_widget_params,
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

patrol_dashboard = gather_dashboard(
    widgets=[
        traj_patrol_events_map_widget,
        td_map_widget,
        patrol_events_bar_chart_widget,
        patrol_events_pie_chart_widget,
    ],
    **patrol_dashboard_params,
)
