# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "2a6d7c0b56f026fd964a75de3d6de8bc8e5934cbeaccc791bedcf87db90ddda3"
import json
import os

from ecoscope_workflows_ext_ecoscope.tasks.io import get_patrol_events
from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.results import gather_dashboard

from ..params import Params


def main(params: Params):
    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    patrol_events = (
        get_patrol_events.validate().partial(**params_dict["patrol_events"]).call()
    )

    groupers = set_groupers.validate().partial(**params_dict["groupers"]).call()

    split_obs = (
        split_groups.validate()
        .partial(df=patrol_events, groupers=groupers, **params_dict["split_obs"])
        .call()
    )

    map_layers = (
        create_map_layer.validate()
        .partial(**params_dict["map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_obs)
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params_dict["ecomaps"])
        .mapvalues(argnames=["geo_layers"], argvalues=map_layers)
    )

    ecomaps_persist = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["ecomaps_persist"],
        )
        .mapvalues(argnames=["text"], argvalues=ecomaps)
    )

    ecomap_widgets = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["ecomap_widgets"])
        .map(argnames=["view", "data"], argvalues=ecomaps_persist)
    )

    ecomap_widgets_merged = (
        merge_widget_views.validate()
        .partial(widgets=ecomap_widgets, **params_dict["ecomap_widgets_merged"])
        .call()
    )

    dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=ecomap_widgets_merged, groupers=groupers, **params_dict["dashboard"]
        )
        .call()
    )

    return dashboard
