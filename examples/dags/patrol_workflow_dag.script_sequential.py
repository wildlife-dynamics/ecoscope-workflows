import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import create_map_layer
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

    patrol_obs = get_patrol_observations.replace(validate=True)(
        **params["patrol_obs"],
    )

    patrol_reloc = process_relocations.replace(validate=True)(
        observations=patrol_obs,
        **params["patrol_reloc"],
    )

    patrol_traj = relocations_to_trajectory.replace(validate=True)(
        relocations=patrol_reloc,
        **params["patrol_traj"],
    )

    patrol_traj_map_layer = create_map_layer.replace(validate=True)(
        geodataframe=patrol_traj,
        **params["patrol_traj_map_layer"],
    )

    patrol_traj_ecomap = draw_ecomap.replace(validate=True)(
        geo_layers=[patrol_traj_map_layer],
        **params["patrol_traj_ecomap"],
    )

    patrol_traj_ecomap_html_url = persist_text.replace(validate=True)(
        text=patrol_traj_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["patrol_traj_ecomap_html_url"],
    )

    patrol_traj_map_widget = create_map_widget_single_view.replace(validate=True)(
        data=patrol_traj_ecomap_html_url,
        **params["patrol_traj_map_widget"],
    )

    patrol_events = get_patrol_events.replace(validate=True)(
        **params["patrol_events"],
    )

    filter_patrol_events = apply_reloc_coord_filter.replace(validate=True)(
        df=patrol_events,
        **params["filter_patrol_events"],
    )

    patrol_events_map_layer = create_map_layer.replace(validate=True)(
        geodataframe=filter_patrol_events,
        **params["patrol_events_map_layer"],
    )

    patrol_events_ecomap = draw_ecomap.replace(validate=True)(
        geo_layers=[patrol_events_map_layer],
        **params["patrol_events_ecomap"],
    )

    patrol_events_ecomap_html_url = persist_text.replace(validate=True)(
        text=patrol_events_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["patrol_events_ecomap_html_url"],
    )

    patrol_events_map_widget = create_map_widget_single_view.replace(validate=True)(
        data=patrol_events_ecomap_html_url,
        **params["patrol_events_map_widget"],
    )

    td = calculate_time_density.replace(validate=True)(
        trajectory_gdf=patrol_traj,
        **params["td"],
    )

    td_map_layer = create_map_layer.replace(validate=True)(
        geodataframe=td,
        **params["td_map_layer"],
    )

    td_ecomap = draw_ecomap.replace(validate=True)(
        geo_layers=[td_map_layer],
        **params["td_ecomap"],
    )

    td_ecomap_html_url = persist_text.replace(validate=True)(
        text=td_ecomap,
        root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        **params["td_ecomap_html_url"],
    )

    td_map_widget = create_map_widget_single_view.replace(validate=True)(
        data=td_ecomap_html_url,
        **params["td_map_widget"],
    )

    patrol_dashboard = gather_dashboard.replace(validate=True)(
        widgets=[patrol_traj_map_widget, patrol_events_map_widget, td_map_widget],
        **params["patrol_dashboard"],
    )

    print(patrol_dashboard)
