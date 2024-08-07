import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("mapvalues_example")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)

    obs = get_subjectgroup_observations.validate().call(**params["obs"])

    groupers = set_groupers.validate().call(**params["groupers"])

    split_obs = (
        split_groups.validate()
        .partial(df=obs, groupers=groupers)
        .call(**params["split_obs"])
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params["ecomaps"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_obs)
    )

    ecomaps_persist = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["ecomaps_persist"],
        )
        .mapvalues(argnames=["text"], argvalues=ecomaps)
    )

    ecomap_widgets = (
        create_map_widget_single_view.validate()
        .partial(**params["ecomap_widgets"])
        .map(argnames=["view", 'data"'], argvalues=ecomaps_persist)
    )

    dashboard = (
        gather_dashboard.validate()
        .partial(widgets=ecomap_widgets, groupers=groupers)
        .call(**params["dashboard"])
    )

    print(dashboard)
