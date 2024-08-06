import argparse
import os
import yaml

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text

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

    obs_a = get_subjectgroup_observations.validate().call(
        **params["obs_a"],
    )

    obs_b = get_subjectgroup_observations.validate().call(
        **params["obs_b"],
    )

    obs_c = get_subjectgroup_observations.validate().call(
        **params["obs_c"],
    )

    ecomaps_mapped_iterable = map(
        lambda kw: draw_ecomap.validate().call(**kw),
        [
            {
                "geodataframe": i,
            }
            | params["ecomaps"]
            for i in [obs_a, obs_b, obs_c]
        ],
    )
    ecomaps = list(ecomaps_mapped_iterable)

    td_ecomap_html_url_mapped_iterable = map(
        lambda kw: persist_text.validate().call(**kw),
        [
            {
                "text": i,
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["td_ecomap_html_url"]
            for i in ecomaps
        ],
    )
    td_ecomap_html_url = list(td_ecomap_html_url_mapped_iterable)

    print(td_ecomap_html_url)
