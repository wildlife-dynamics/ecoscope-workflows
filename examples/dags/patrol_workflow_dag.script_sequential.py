import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter
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
    # FIXME: first pass assumes tasks are already in topological order

    patrol_obs = get_patrol_observations.validate().call(
        **params["patrol_obs"],
    )

    patrol_reloc = process_relocations.validate().call(
        observations=patrol_obs,
        **params["patrol_reloc"],
    )

    patrol_traj = relocations_to_trajectory.validate().call(
        relocations=patrol_reloc,
        **params["patrol_traj"],
    )

    patrol_traj_ecomap = draw_ecomap.validate().call(
        geodataframe=patrol_traj,
        **params["patrol_traj_ecomap"],
    )

    patrol_traj_ecomap_html_url = persist_text.validate().call(
        text=patrol_traj_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["patrol_traj_ecomap_html_url"],
    )

    patrol_traj_map_widget = create_map_widget_single_view.validate().call(
        data=patrol_traj_ecomap_html_url,
        **params["patrol_traj_map_widget"],
    )

    patrol_events = get_patrol_events.validate().call(
        **params["patrol_events"],
    )

    filter_patrol_events = apply_reloc_coord_filter.validate().call(
        df=patrol_events,
        **params["filter_patrol_events"],
    )

    patrol_events_ecomap = draw_ecomap.validate().call(
        geodataframe=filter_patrol_events,
        **params["patrol_events_ecomap"],
    )

    patrol_events_ecomap_html_url = persist_text.validate().call(
        text=patrol_events_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["patrol_events_ecomap_html_url"],
    )

    patrol_events_map_widget = create_map_widget_single_view.validate().call(
        data=patrol_events_ecomap_html_url,
        **params["patrol_events_map_widget"],
    )

    td = calculate_time_density.validate().call(
        trajectory_gdf=patrol_traj,
        **params["td"],
    )

    td_ecomap = draw_ecomap.validate().call(
        geodataframe=td,
        **params["td_ecomap"],
    )

    td_ecomap_html_url = persist_text.validate().call(
        text=td_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["td_ecomap_html_url"],
    )

    td_map_widget = create_map_widget_single_view.validate().call(
        data=td_ecomap_html_url,
        **params["td_map_widget"],
    )

    patrol_dashboard = gather_dashboard.validate().call(
        widgets=[patrol_traj_map_widget, patrol_events_map_widget, td_map_widget],
        **params["patrol_dashboard"],
    )

    print(patrol_dashboard)
