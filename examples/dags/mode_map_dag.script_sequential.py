import argparse
from functools import partial
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
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

    obs_a = get_subjectgroup_observations.replace(validate=True)(
        **params["obs_a"],
    )

    obs_b = get_subjectgroup_observations.replace(validate=True)(
        **params["obs_b"],
    )

    obs_c = get_subjectgroup_observations.replace(validate=True)(
        **params["obs_c"],
    )

    ecomaps_partial = partial(draw_ecomap.replace(validate=True), **params["ecomaps"])
    ecomaps_mapped_iterable = map(ecomaps_partial, [obs_a, obs_b, obs_c])
    ecomaps = list(ecomaps_mapped_iterable)

    print(ecomaps)
