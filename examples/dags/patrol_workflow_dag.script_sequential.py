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

    groupers = set_groupers.validate().call(**params["groupers"])

    patrol_obs = get_patrol_observations.validate().call(**params["patrol_obs"])

    patrol_reloc = (
        process_relocations.validate()
        .partial(observations=patrol_obs)
        .call(**params["patrol_reloc"])
    )

    patrol_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=patrol_reloc)
        .call(**params["patrol_traj"])
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=patrol_traj)
        .call(**params["traj_add_temporal_index"])
    )

    split_patrol_traj_groups = (
        split_groups.validate()
        .partial(df=traj_add_temporal_index, groupers=groupers)
        .call(**params["split_patrol_traj_groups"])
    )

    patrol_traj_map_layers = (
        create_map_layer.validate()
        .partial(**params["patrol_traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_traj_groups)
    )

    patrol_events = get_patrol_events.validate().call(**params["patrol_events"])

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(df=patrol_events)
        .call(**params["filter_patrol_events"])
    )

    pe_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=filter_patrol_events)
        .call(**params["pe_add_temporal_index"])
    )

    split_pe_groups = (
        split_groups.validate()
        .partial(df=pe_add_temporal_index, groupers=groupers)
        .call(**params["split_pe_groups"])
    )

    patrol_events_map_layers = (
        create_map_layer.validate()
        .partial(**params["patrol_events_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_pe_groups)
    )

    combined_traj_and_pe_map_layers = (
        groupbykey.validate()
        .partial(iterables=[patrol_traj_map_layers, patrol_events_map_layers])
        .call(**params["combined_traj_and_pe_map_layers"])
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
        .partial(widgets=traj_pe_map_widgets_single_views)
        .call(**params["traj_pe_grouped_map_widget"])
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
        .partial(widgets=total_patrols_sv_widgets)
        .call(**params["total_patrols_grouped_sv_widget"])
    )

    patrol_events_bar_chart = (
        draw_time_series_bar_chart.validate()
        .partial(dataframe=filter_patrol_events)
        .call(**params["patrol_events_bar_chart"])
    )

    patrol_events_bar_chart_html_url = (
        persist_text.validate()
        .partial(
            text=patrol_events_bar_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        )
        .call(**params["patrol_events_bar_chart_html_url"])
    )

    patrol_events_bar_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(data=patrol_events_bar_chart_html_url)
        .call(**params["patrol_events_bar_chart_widget"])
    )

    patrol_events_pie_chart = (
        draw_pie_chart.validate()
        .partial(dataframe=filter_patrol_events)
        .call(**params["patrol_events_pie_chart"])
    )

    patrol_events_pie_chart_html_url = (
        persist_text.validate()
        .partial(
            text=patrol_events_pie_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        )
        .call(**params["patrol_events_pie_chart_html_url"])
    )

    patrol_events_pie_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(data=patrol_events_pie_chart_html_url)
        .call(**params["patrol_events_pie_chart_widget"])
    )

    td = (
        calculate_time_density.validate()
        .partial(trajectory_gdf=patrol_traj)
        .call(**params["td"])
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=td)
        .call(**params["td_map_layer"])
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=td_map_layer)
        .call(**params["td_ecomap"])
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(text=td_ecomap, root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"])
        .call(**params["td_ecomap_html_url"])
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=td_ecomap_html_url)
        .call(**params["td_map_widget"])
    )

    patrol_dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=[
                traj_pe_grouped_map_widget,
                td_map_widget,
                patrol_events_bar_chart_widget,
                patrol_events_pie_chart_widget,
                total_patrols_grouped_sv_widget,
            ],
            groupers=groupers,
        )
        .call(**params["patrol_dashboard"])
    )

    print(patrol_dashboard)
