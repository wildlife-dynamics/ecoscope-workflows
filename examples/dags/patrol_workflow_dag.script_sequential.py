import argparse
import yaml

from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import gather_dashboard
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter

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

    patrol_ecomap = draw_ecomap.replace(validate=True)(
        geodataframe=patrol_traj,
        **params["patrol_ecomap"],
    )

    patrol_ecomap_html_url = persist_text.replace(validate=True)(
        text=patrol_ecomap,
        **params["patrol_ecomap_html_url"],
    )

    patrol_map_widget = create_map_widget_single_view.replace(validate=True)(
        data=patrol_ecomap_html_url,
        **params["patrol_map_widget"],
    )

    patrol_dashboard = gather_dashboard.replace(validate=True)(
        widgets=patrol_map_widget,
        **params["patrol_dashboard"],
    )

    patrol_events = get_patrol_events.replace(validate=True)(
        **params["patrol_events"],
    )

    filter_patrol_events = apply_reloc_coord_filter.replace(validate=True)(
        df=patrol_events,
        **params["filter_patrol_events"],
    )

    print(filter_patrol_events)
