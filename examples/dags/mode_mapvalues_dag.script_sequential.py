import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view

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
    # FIXME: first pass assumes tasks are already in topological order

    obs = get_subjectgroup_observations.replace(validate=True)(
        **params["obs"],
    )

    groupers = set_groupers.replace(validate=True)(
        **params["groupers"],
    )

    split_obs = split_groups.replace(validate=True)(
        df=obs,
        groupers=groupers,
        **params["split_obs"],
    )

    ecomaps_mapped_iterable = map(
        lambda kv: (kv[0], draw_ecomap.replace(validate=True)(**kv[1])),
        [
            (
                k,
                {
                    "geodataframe": geodataframe,
                }
                | params["ecomaps"],
            )
            for (k, geodataframe) in split_obs
        ],
    )
    ecomaps = list(ecomaps_mapped_iterable)

    ecomaps_persist_mapped_iterable = map(
        lambda kv: (kv[0], persist_text.replace(validate=True)(**kv[1])),
        [
            (
                k,
                {
                    "text": text,
                    "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                }
                | params["ecomaps_persist"],
            )
            for (k, text) in ecomaps
        ],
    )
    ecomaps_persist = list(ecomaps_persist_mapped_iterable)

    ecomap_widgets_mapped_iterable = map(
        lambda kw: create_map_widget_single_view.replace(validate=True)(**kw),
        [
            {
                "view": view,
                "data": data,
            }
            | params["ecomap_widgets"]
            for (view, data) in ecomaps_persist
        ],
    )
    ecomap_widgets = list(ecomap_widgets_mapped_iterable)

    print(ecomap_widgets)