import argparse
from functools import partial

import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.parallel import split_groups
from ecoscope_workflows.tasks.results import draw_ecomap

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("map_example")
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

    split = split_groups.replace(validate=True)(
        df=obs,
        **params["split"],
    )

    ecomaps_partial = partial(draw_ecomap.replace(validate=True), **params["ecomaps"])
    ecomaps_mapped_iterable = map(ecomaps_partial, split)
    ecomaps = list(ecomaps_mapped_iterable)

    print(ecomaps)
