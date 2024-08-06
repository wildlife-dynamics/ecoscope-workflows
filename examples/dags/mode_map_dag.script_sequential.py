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

    obs_a = get_subjectgroup_observations.validate().call(**params["obs_a"])

    obs_b = get_subjectgroup_observations.validate().call(**params["obs_b"])

    obs_c = get_subjectgroup_observations.validate().call(**params["obs_c"])

    ecomaps = draw_ecomap.validate().map(
        argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c]
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
