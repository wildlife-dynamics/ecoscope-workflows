# ruff: noqa: E402

"""WARNING: This file is generated in a testing context and should not be used in production.
Lines specific to the testing context are marked with a test tube emoji (🧪) to indicate
that they would not be included (or would be different) in the production version of this file.
"""

import os
import warnings  # 🧪
from ecoscope_workflows_core.testing import create_task_magicmock  # 🧪


get_patrol_events = create_task_magicmock(  # 🧪
    anchor="ecoscope_workflows_ext_ecoscope.tasks.io",  # 🧪
    func_name="get_patrol_events",  # 🧪
)  # 🧪
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
    warnings.warn("This test script should not be used in production!")  # 🧪

    patrol_events = (
        get_patrol_events.validate()
        .partial(**params.patrol_events.model_dump(exclude_unset=True))
        .call()
    )

    groupers = (
        set_groupers.validate()
        .partial(**params.groupers.model_dump(exclude_unset=True))
        .call()
    )

    split_obs = (
        split_groups.validate()
        .partial(
            df=patrol_events,
            groupers=groupers,
            **params.split_obs.model_dump(exclude_unset=True),
        )
        .call()
    )

    map_layers = (
        create_map_layer.validate()
        .partial(**params.map_layers.model_dump(exclude_unset=True))
        .mapvalues(argnames=["geodataframe"], argvalues=split_obs)
    )

    ecomaps = (
        draw_ecomap.validate()
        .partial(**params.ecomaps.model_dump(exclude_unset=True))
        .mapvalues(argnames=["geo_layers"], argvalues=map_layers)
    )

    ecomaps_persist = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.ecomaps_persist.model_dump(exclude_unset=True),
        )
        .mapvalues(argnames=["text"], argvalues=ecomaps)
    )

    ecomap_widgets = (
        create_map_widget_single_view.validate()
        .partial(**params.ecomap_widgets.model_dump(exclude_unset=True))
        .map(argnames=["view", "data"], argvalues=ecomaps_persist)
    )

    ecomap_widgets_merged = (
        merge_widget_views.validate()
        .partial(
            widgets=ecomap_widgets,
            **params.ecomap_widgets_merged.model_dump(exclude_unset=True),
        )
        .call()
    )

    dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=ecomap_widgets_merged,
            groupers=groupers,
            **params.dashboard.model_dump(exclude_unset=True),
        )
        .call()
    )

    return dashboard
