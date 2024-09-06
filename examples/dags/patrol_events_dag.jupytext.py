# ruff: noqa: E402

# %% [markdown]
# # Patrol Events Workflow
# TODO: top level description

# %% [markdown]
# ## Imports

import os
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter
from ecoscope_workflows.tasks.transformation import add_temporal_index
from ecoscope_workflows.tasks.transformation import apply_color_map
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows.tasks.results import create_plot_widget_single_view
from ecoscope_workflows.tasks.analysis import create_meshgrid
from ecoscope_workflows.tasks.analysis import calculate_feature_density
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import draw_pie_chart
from ecoscope_workflows.tasks.results import merge_widget_views
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


groupers = set_groupers.partial(**groupers_params).call()


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
# ## Patrol Events Colormap

# %%
# parameters

pe_colormap_params = dict(
    df=...,
    input_column_name=...,
    colormap=...,
    output_column_name=...,
)

# %%
# call the task


pe_colormap = apply_color_map.partial(
    geodataframe=filter_patrol_events, **pe_colormap_params
).call()


# %% [markdown]
# ## Create map layer from Patrol Events

# %%
# parameters

pe_map_layer_params = dict(
    layer_style=...,
)

# %%
# call the task


pe_map_layer = create_map_layer.partial(
    geodataframe=pe_colormap, **pe_map_layer_params
).call()


# %% [markdown]
# ## Draw Ecomap from Time Density

# %%
# parameters

pe_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
)

# %%
# call the task


pe_ecomap = draw_ecomap.partial(geo_layers=pe_map_layer, **pe_ecomap_params).call()


# %% [markdown]
# ## Persist Ecomap as Text

# %%
# parameters

pe_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task


pe_ecomap_html_url = persist_text.partial(
    text=pe_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **pe_ecomap_html_url_params,
).call()


# %% [markdown]
# ## Create Time Density Map Widget

# %%
# parameters

pe_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


pe_map_widget = create_map_widget_single_view.partial(
    data=pe_ecomap_html_url, **pe_map_widget_params
).call()


# %% [markdown]
# ## Draw Time Series Bar Chart for Patrols Events

# %%
# parameters

pe_bar_chart_params = dict(
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


pe_bar_chart = draw_time_series_bar_chart.partial(
    dataframe=filter_patrol_events, **pe_bar_chart_params
).call()


# %% [markdown]
# ## Persist Patrols Bar Chart as Text

# %%
# parameters

pe_bar_chart_html_url_params = dict(
    filename=...,
)

# %%
# call the task


pe_bar_chart_html_url = persist_text.partial(
    text=pe_bar_chart,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **pe_bar_chart_html_url_params,
).call()


# %% [markdown]
# ## Create Plot Widget for Patrol Events

# %%
# parameters

pe_bar_chart_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


pe_bar_chart_widget = create_plot_widget_single_view.partial(
    data=pe_bar_chart_html_url, **pe_bar_chart_widget_params
).call()


# %% [markdown]
# ## Create Patrol Events Meshgrid

# %%
# parameters

pe_meshgrid_params = dict(
    cell_width=...,
    cell_height=...,
    intersecting_only=...,
    existing_grid=...,
)

# %%
# call the task


pe_meshgrid = create_meshgrid.partial(
    aoi=filter_patrol_events, **pe_meshgrid_params
).call()


# %% [markdown]
# ## Patrol Events Feature Density

# %%
# parameters

pe_feature_density_params = dict(
    geometry_type=...,
)

# %%
# call the task


pe_feature_density = calculate_feature_density.partial(
    geodataframe=filter_patrol_events, meshgrid=pe_meshgrid, **pe_feature_density_params
).call()


# %% [markdown]
# ## Feature Density Colormap

# %%
# parameters

fd_colormap_params = dict(
    df=...,
    input_column_name=...,
    colormap=...,
    output_column_name=...,
)

# %%
# call the task


fd_colormap = apply_color_map.partial(
    geodataframe=pe_feature_density, **fd_colormap_params
).call()


# %% [markdown]
# ## Create map layer from Feature Density

# %%
# parameters

fd_map_layer_params = dict(
    layer_style=...,
)

# %%
# call the task


fd_map_layer = create_map_layer.partial(
    geodataframe=fd_colormap, **fd_map_layer_params
).call()


# %% [markdown]
# ## Draw Ecomap from Feature Density

# %%
# parameters

fd_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
)

# %%
# call the task


fd_ecomap = draw_ecomap.partial(geo_layers=fd_map_layer, **fd_ecomap_params).call()


# %% [markdown]
# ## Persist Feature Density Ecomap as Text

# %%
# parameters

fd_ecomap_html_url_params = dict(
    filename=...,
)

# %%
# call the task


fd_ecomap_html_url = persist_text.partial(
    text=fd_ecomap,
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **fd_ecomap_html_url_params,
).call()


# %% [markdown]
# ## Create Feature Density Map Widget

# %%
# parameters

fd_map_widget_params = dict(
    title=...,
    view=...,
)

# %%
# call the task


fd_map_widget = create_map_widget_single_view.partial(
    data=fd_ecomap_html_url, **fd_map_widget_params
).call()


# %% [markdown]
# ## Split Patrol Events by Group

# %%
# parameters

split_patrol_event_groups_params = dict()

# %%
# call the task


split_patrol_event_groups = split_groups.partial(
    df=pe_add_temporal_index, groupers=groupers, **split_patrol_event_groups_params
).call()


# %% [markdown]
# ## Grouped Patrol Events Colormap

# %%
# parameters

grouped_pe_colormap_params = dict(
    df=...,
    input_column_name=...,
    colormap=...,
    output_column_name=...,
)

# %%
# call the task


grouped_pe_colormap = apply_color_map.partial(**grouped_pe_colormap_params).mapvalues(
    argnames=["geodataframe"], argvalues=split_patrol_event_groups
)


# %% [markdown]
# ## Create map layer from grouped Patrol Events

# %%
# parameters

grouped_pe_map_layer_params = dict(
    layer_style=...,
)

# %%
# call the task


grouped_pe_map_layer = create_map_layer.partial(
    **grouped_pe_map_layer_params
).mapvalues(argnames=["geodataframe"], argvalues=grouped_pe_colormap)


# %% [markdown]
# ## Draw Ecomap from grouped Patrol Events

# %%
# parameters

grouped_pe_ecomap_params = dict(
    geo_layers=...,
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
)

# %%
# call the task


grouped_pe_ecomap = draw_ecomap.partial(**grouped_pe_ecomap_params).mapvalues(
    argnames=["geodataframe"], argvalues=grouped_pe_map_layer
)


# %% [markdown]
# ## Persist grouped Patrol Events Ecomap as Text

# %%
# parameters

grouped_pe_ecomap_html_url_params = dict(
    root_path=...,
    filename=...,
)

# %%
# call the task


grouped_pe_ecomap_html_url = persist_text.partial(
    **grouped_pe_ecomap_html_url_params
).mapvalues(argnames=["text"], argvalues=grouped_pe_ecomap)


# %% [markdown]
# ## Create grouped Patrol Events Map Widget

# %%
# parameters

grouped_pe_map_widget_params = dict(
    title=...,
)

# %%
# call the task


grouped_pe_map_widget = create_map_widget_single_view.partial(
    **grouped_pe_map_widget_params
).map(argnames=["view", "data"], argvalues=grouped_pe_ecomap_html_url)


# %% [markdown]
# ## Draw Pie Chart for Patrols Events

# %%
# parameters

grouped_pe_pie_chart_params = dict(
    value_column=...,
    label_column=...,
    color_column=...,
    plot_style=...,
    layout_style=...,
)

# %%
# call the task


grouped_pe_pie_chart = draw_pie_chart.partial(**grouped_pe_pie_chart_params).mapvalues(
    argnames=["dataframe"], argvalues=split_patrol_event_groups
)


# %% [markdown]
# ## Persist Patrols Pie Chart as Text

# %%
# parameters

grouped_pe_pie_chart_html_urls_params = dict(
    filename=...,
)

# %%
# call the task


grouped_pe_pie_chart_html_urls = persist_text.partial(
    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
    **grouped_pe_pie_chart_html_urls_params,
).mapvalues(argnames=["text"], argvalues=grouped_pe_pie_chart)


# %% [markdown]
# ## Create Plot Widget for Patrol Events

# %%
# parameters

grouped_pe_pie_chart_widgets_params = dict(
    title=...,
)

# %%
# call the task


grouped_pe_pie_chart_widgets = create_plot_widget_single_view.partial(
    **grouped_pe_pie_chart_widgets_params
).map(argnames=["view", "data"], argvalues=grouped_pe_pie_chart_html_urls)


# %% [markdown]
# ## Merge Pie Chart Widget Views

# %%
# parameters

grouped_pe_pie_widget_grouped_params = dict()

# %%
# call the task


grouped_pe_pie_widget_grouped = merge_widget_views.partial(
    widgets=grouped_pe_pie_chart_widgets, **grouped_pe_pie_widget_grouped_params
).call()


# %% [markdown]
# ## Grouped Patrol Events Feature Density

# %%
# parameters

grouped_pe_feature_density_params = dict(
    geometry_type=...,
)

# %%
# call the task


grouped_pe_feature_density = calculate_feature_density.partial(
    meshgrid=pe_meshgrid, **grouped_pe_feature_density_params
).map(argnames=["geodataframe"], argvalues=split_patrol_event_groups)


# %% [markdown]
# ## Create map layer from Feature Density

# %%
# parameters

grouped_fd_map_layer_params = dict(
    layer_style=...,
)

# %%
# call the task


grouped_fd_map_layer = create_map_layer.partial(
    **grouped_fd_map_layer_params
).mapvalues(argnames=["geodataframe"], argvalues=pe_feature_density)


# %% [markdown]
# ## Draw Ecomap from Feature Density

# %%
# parameters

grouped_fd_ecomap_params = dict(
    tile_layer=...,
    static=...,
    title=...,
    north_arrow_style=...,
)

# %%
# call the task


grouped_fd_ecomap = draw_ecomap.partial(**grouped_fd_ecomap_params).mapvalues(
    argnames=["geo_layers"], argvalues=grouped_fd_map_layer
)


# %% [markdown]
# ## Persist Feature Density Ecomap as Text

# %%
# parameters

grouped_fd_ecomap_html_url_params = dict(
    root_path=...,
    filename=...,
)

# %%
# call the task


grouped_fd_ecomap_html_url = persist_text.partial(
    **grouped_fd_ecomap_html_url_params
).mapvalues(argnames=["text"], argvalues=grouped_fd_ecomap)


# %% [markdown]
# ## Create Feature Density Map Widget

# %%
# parameters

grouped_fd_map_widget_params = dict(
    title=...,
)

# %%
# call the task


grouped_fd_map_widget = create_map_widget_single_view.partial(
    **grouped_fd_map_widget_params
).map(argnames=["view", "data"], argvalues=grouped_fd_ecomap_html_url)


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
        pe_map_widget,
        pe_bar_chart_widget,
        fd_map_widget,
        grouped_pe_map_widget,
        grouped_pe_pie_widget_grouped,
        grouped_fd_map_widget,
    ],
    groupers=groupers,
    **patrol_dashboard_params,
).call()
