import os

from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text


def main(params: dict):
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

    return td_ecomap_html_url
