# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "1f5d74c437542ff7b0cb9d58b9d2ceac5825c66bdc6e0efad0d3534eb72e3cf0"
import json
import os

from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text

from ..params import Params


def main(params: Params):
    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    obs_a = (
        get_subjectgroup_observations.validate().partial(**params_dict["obs_a"]).call()
    )

    obs_b = (
        get_subjectgroup_observations.validate().partial(**params_dict["obs_b"]).call()
    )

    obs_c = (
        get_subjectgroup_observations.validate().partial(**params_dict["obs_c"]).call()
    )

    map_layers = (
        create_map_layer.validate()
        .partial(**params_dict["map_layers"])
        .map(argnames=["geodataframe"], argvalues=[obs_a, obs_b, obs_c])
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params_dict["ecomaps"])
        .map(argnames=["geo_layers"], argvalues=map_layers)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["td_ecomap_html_url"],
        )
        .map(argnames=["text"], argvalues=ecomaps)
    )

    return td_ecomap_html_url
