import argparse
import os
import yaml

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
from ecoscope_workflows.tasks.analysis import dataframe_column_nunique
from ecoscope_workflows.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows.tasks.analysis import dataframe_column_sum
from ecoscope_workflows.tasks.transformation import with_unit
from ecoscope_workflows.tasks.analysis import dataframe_column_mean
from ecoscope_workflows.tasks.analysis import dataframe_column_max
from ecoscope_workflows.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows.tasks.results import create_plot_widget_single_view
from ecoscope_workflows.tasks.results import draw_pie_chart
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("patrol_workflow")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)

    groupers = set_groupers.validate().partial(**params["groupers"]).call()

    patrol_obs = (
        get_patrol_observations.validate().partial(**params["patrol_obs"]).call()
    )

    patrol_reloc = (
        process_relocations.validate()
        .partial(observations=patrol_obs, **params["patrol_reloc"])
        .call()
    )

    patrol_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=patrol_reloc, **params["patrol_traj"])
        .call()
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=patrol_traj, **params["traj_add_temporal_index"])
        .call()
    )

    split_patrol_traj_groups = (
        split_groups.validate()
        .partial(
            df=traj_add_temporal_index,
            groupers=groupers,
            **params["split_patrol_traj_groups"],
        )
        .call()
    )

    patrol_traj_map_layers = (
        create_map_layer.validate()
        .partial(**params["patrol_traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_traj_groups)
    )

    patrol_events = (
        get_patrol_events.validate().partial(**params["patrol_events"]).call()
    )

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(df=patrol_events, **params["filter_patrol_events"])
        .call()
    )

    pe_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=filter_patrol_events, **params["pe_add_temporal_index"])
        .call()
    )

    split_pe_groups = (
        split_groups.validate()
        .partial(
            df=pe_add_temporal_index, groupers=groupers, **params["split_pe_groups"]
        )
        .call()
    )

    patrol_events_map_layers = (
        create_map_layer.validate()
        .partial(**params["patrol_events_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_pe_groups)
    )

    combined_traj_and_pe_map_layers = (
        groupbykey.validate()
        .partial(
            iterables=[patrol_traj_map_layers, patrol_events_map_layers],
            **params["combined_traj_and_pe_map_layers"],
        )
        .call()
    )

    traj_patrol_events_ecomap = (
        draw_ecomap.validate()
        .partial(**params["traj_patrol_events_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=combined_traj_and_pe_map_layers)
    )

    traj_pe_ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["traj_pe_ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_patrol_events_ecomap)
    )

    traj_pe_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(**params["traj_pe_map_widgets_single_views"])
        .map(argnames=["view", "data"], argvalues=traj_pe_ecomap_html_urls)
    )

    traj_pe_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=traj_pe_map_widgets_single_views,
            **params["traj_pe_grouped_map_widget"],
        )
        .call()
    )

    total_patrols = (
        dataframe_column_nunique.validate()
        .partial(**params["total_patrols"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrols_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["total_patrols_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrols)
    )

    total_patrols_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrols_sv_widgets,
            **params["total_patrols_grouped_sv_widget"],
        )
        .call()
    )

    total_patrol_time = (
        dataframe_column_sum.validate()
        .partial(**params["total_patrol_time"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_time_converted = (
        with_unit.validate()
        .partial(**params["total_patrol_time_converted"])
        .mapvalues(argnames=["value"], argvalues=total_patrol_time)
    )

    total_patrol_time_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["total_patrol_time_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrol_time_converted)
    )

    patrol_time_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_time_sv_widgets, **params["patrol_time_grouped_widget"]
        )
        .call()
    )

    total_patrol_dist = (
        dataframe_column_sum.validate()
        .partial(**params["total_patrol_dist"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_dist_converted = (
        with_unit.validate()
        .partial(**params["total_patrol_dist_converted"])
        .mapvalues(argnames=["value"], argvalues=total_patrol_dist)
    )

    total_patrol_dist_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["total_patrol_dist_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrol_dist_converted)
    )

    patrol_dist_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_dist_sv_widgets, **params["patrol_dist_grouped_widget"]
        )
        .call()
    )

    avg_speed = (
        dataframe_column_mean.validate()
        .partial(**params["avg_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    average_speed_converted = (
        with_unit.validate()
        .partial(**params["average_speed_converted"])
        .mapvalues(argnames=["value"], argvalues=avg_speed)
    )

    avg_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["avg_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=average_speed_converted)
    )

    avg_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(widgets=avg_speed_sv_widgets, **params["avg_speed_grouped_widget"])
        .call()
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    max_speed_converted = (
        with_unit.validate()
        .partial(**params["max_speed_converted"])
        .mapvalues(argnames=["value"], argvalues=max_speed)
    )

    max_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["max_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=max_speed_converted)
    )

    max_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(widgets=max_speed_sv_widgets, **params["max_speed_grouped_widget"])
        .call()
    )

    patrol_events_bar_chart = (
        draw_time_series_bar_chart.validate()
        .partial(dataframe=filter_patrol_events, **params["patrol_events_bar_chart"])
        .call()
    )

    patrol_events_bar_chart_html_url = (
        persist_text.validate()
        .partial(
            text=patrol_events_bar_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["patrol_events_bar_chart_html_url"],
        )
        .call()
    )

    patrol_events_bar_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(
            data=patrol_events_bar_chart_html_url,
            **params["patrol_events_bar_chart_widget"],
        )
        .call()
    )

    patrol_events_pie_chart = (
        draw_pie_chart.validate()
        .partial(**params["patrol_events_pie_chart"])
        .mapvalues(argnames=["dataframe"], argvalues=split_pe_groups)
    )

    pe_pie_chart_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["pe_pie_chart_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=patrol_events_pie_chart)
    )

    patrol_events_pie_chart_widgets = (
        create_plot_widget_single_view.validate()
        .partial(**params["patrol_events_pie_chart_widgets"])
        .map(argnames=["view", "data"], argvalues=pe_pie_chart_html_urls)
    )

    patrol_events_pie_widget_grouped = (
        merge_widget_views.validate()
        .partial(
            widgets=patrol_events_pie_chart_widgets,
            **params["patrol_events_pie_widget_grouped"],
        )
        .call()
    )

    td = (
        calculate_time_density.validate()
        .partial(trajectory_gdf=patrol_traj, **params["td"])
        .call()
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=td, **params["td_map_layer"])
        .call()
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=td_map_layer, **params["td_ecomap"])
        .call()
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=td_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["td_ecomap_html_url"],
        )
        .call()
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=td_ecomap_html_url, **params["td_map_widget"])
        .call()
    )

    patrol_dashboard = (
        gather_dashboard.validate()
        .partial(
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
            **params["patrol_dashboard"],
        )
        .call()
    )

    print(patrol_dashboard)
