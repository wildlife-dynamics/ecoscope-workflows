import argparse
import os
import yaml

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

    patrol_traj_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=patrol_traj)
        .call(**params["patrol_traj_map_layer"])
    )

    patrol_events = get_patrol_events.validate().call(**params["patrol_events"])

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(df=patrol_events)
        .call(**params["filter_patrol_events"])
    )

    patrol_events_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=filter_patrol_events)
        .call(**params["patrol_events_map_layer"])
    )

    traj_patrol_events_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=[patrol_traj_map_layer, patrol_events_map_layer])
        .call(**params["traj_patrol_events_ecomap"])
    )

    traj_pe_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=traj_patrol_events_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        )
        .call(**params["traj_pe_ecomap_html_url"])
    )

    traj_patrol_events_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=traj_pe_ecomap_html_url)
        .call(**params["traj_patrol_events_map_widget"])
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
                traj_patrol_events_map_widget,
                td_map_widget,
                patrol_events_bar_chart_widget,
                patrol_events_pie_chart_widget,
            ]
        )
        .call(**params["patrol_dashboard"])
    )

    print(patrol_dashboard)
