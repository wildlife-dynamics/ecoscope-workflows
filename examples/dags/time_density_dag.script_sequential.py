import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("calculate_time_density")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)
    # FIXME: first pass assumes tasks are already in topological order

    obs = get_subjectgroup_observations.replace(validate=True)(
        **params["obs"],
    )

    reloc = process_relocations.replace(validate=True)(
        observations=obs,
        **params["reloc"],
    )

    traj = relocations_to_trajectory.replace(validate=True)(
        relocations=reloc,
        **params["traj"],
    )

    td = calculate_time_density.replace(validate=True)(
        trajectory_gdf=traj,
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

    td_dashboard = gather_dashboard.replace(validate=True)(
        widgets=td_map_widget,
        **params["td_dashboard"],
    )

    print(td_dashboard)
