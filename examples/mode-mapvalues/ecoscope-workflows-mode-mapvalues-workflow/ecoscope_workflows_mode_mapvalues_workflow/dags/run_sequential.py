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
    patrol_events = (
        get_patrol_events.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_events"])
        .call()
    )

    groupers = (
        set_groupers.validate()
        .partial(**params.model_dump(exclude_unset=True)["groupers"])
        .call()
    )

    split_obs = (
        split_groups.validate()
        .partial(
            df=patrol_events,
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["split_obs"],
        )
        .call()
    )

    map_layers = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_obs)
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params.model_dump(exclude_unset=True)["ecomaps"])
        .mapvalues(argnames=["geo_layers"], argvalues=map_layers)
    )

    ecomaps_persist = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["ecomaps_persist"],
        )
        .mapvalues(argnames=["text"], argvalues=ecomaps)
    )

    ecomap_widgets = (
        create_map_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["ecomap_widgets"])
        .map(argnames=["view", "data"], argvalues=ecomaps_persist)
    )

    ecomap_widgets_merged = (
        merge_widget_views.validate()
        .partial(
            widgets=ecomap_widgets,
            **params.model_dump(exclude_unset=True)["ecomap_widgets_merged"],
        )
        .call()
    )

    dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=ecomap_widgets_merged,
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["dashboard"],
        )
        .call()
    )

    return dashboard
