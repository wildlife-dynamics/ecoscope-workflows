import argparse
import os
import yaml

from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.transformation import add_temporal_index
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.groupby import groupbykey
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views

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

    subject_obs = get_subjectgroup_observations.validate().call(**params["subject_obs"])

    subject_reloc = (
        process_relocations.validate()
        .partial(observations=subject_obs)
        .call(**params["subject_reloc"])
    )

    subject_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=subject_reloc)
        .call(**params["subject_traj"])
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=subject_traj)
        .call(**params["traj_add_temporal_index"])
    )

    split_subject_traj_groups = (
        split_groups.validate()
        .partial(df=traj_add_temporal_index, groupers=groupers)
        .call(**params["split_subject_traj_groups"])
    )

    traj_map_layers = (
        create_map_layer.validate()
        .partial(**params["traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_subject_traj_groups)
    )

    combined_traj_map_layers = (
        groupbykey.validate()
        .partial(iterables=traj_map_layers)
        .call(**params["combined_traj_map_layers"])
    )

    traj_ecomap = (
        draw_ecomap.validate()
        .partial(**params["traj_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=combined_traj_map_layers)
    )

    ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_ecomap)
    )

    traj_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(**params["traj_map_widgets_single_views"])
        .map(argnames=["view", "data"], argvalues=ecomap_html_urls)
    )

    traj_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(widgets=traj_map_widgets_single_views)
        .call(**params["traj_grouped_map_widget"])
    )

    print(traj_grouped_map_widget)
