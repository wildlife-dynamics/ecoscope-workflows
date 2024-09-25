import os

from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text

from ..params import Params


def main(params: Params):
    obs_a = (
        get_subjectgroup_observations.validate()
        .partial(**params.model_dump(exclude_unset=True)["obs_a"])
        .call()
    )

    obs_b = (
        get_subjectgroup_observations.validate()
        .partial(**params.model_dump(exclude_unset=True)["obs_b"])
        .call()
    )

    obs_c = (
        get_subjectgroup_observations.validate()
        .partial(**params.model_dump(exclude_unset=True)["obs_c"])
        .call()
    )

    map_layers = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["map_layers"])
        .map(argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c])
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params.model_dump(exclude_unset=True)["ecomaps"])
        .map(argnames=["geo_layers"], argvalues=map_layers)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["td_ecomap_html_url"],
        )
        .map(argnames=["text"], argvalues=ecomaps)
    )

    return td_ecomap_html_url
