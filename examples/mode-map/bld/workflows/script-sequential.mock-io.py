import argparse
import os
import yaml

from ecoscope_workflows.testing import create_task_magicmock

# from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text

get_subjectgroup_observations = create_task_magicmock(
    "ecoscope_workflows.tasks.io",
    "get_subjectgroup_observations",
)

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

    obs_a = get_subjectgroup_observations.validate().partial(**params["obs_a"]).call()

    obs_b = get_subjectgroup_observations.validate().partial(**params["obs_b"]).call()

    obs_c = get_subjectgroup_observations.validate().partial(**params["obs_c"]).call()

    map_layers = (
        create_map_layer.validate()
        .partial(**params["map_layers"])
        .map(argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c])
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params["ecomaps"])
        .map(argnames=["geo_layers"], argvalues=map_layers)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["td_ecomap_html_url"],
        )
        .map(argnames=["text"], argvalues=ecomaps)
    )

    print(td_ecomap_html_url)
