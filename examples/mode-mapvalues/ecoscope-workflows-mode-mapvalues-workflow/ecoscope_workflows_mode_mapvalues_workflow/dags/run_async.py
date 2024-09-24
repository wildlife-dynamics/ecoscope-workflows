import os

from ecoscope_workflows_core.graph import DependsOn, Graph, Node

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
    dependencies = {
        "patrol_events": [],
        "groupers": [],
        "split_obs": ["patrol_events", "groupers"],
        "map_layers": ["split_obs"],
        "ecomaps": ["map_layers"],
        "ecomaps_persist": ["ecomaps"],
        "ecomap_widgets": ["ecomaps_persist"],
        "ecomap_widgets_merged": ["ecomap_widgets"],
        "dashboard": ["ecomap_widgets_merged", "groupers"],
    }

    nodes = {
        "patrol_events": Node(
            async_task=get_patrol_events.validate().set_executor("lithops"),
            partial=params.patrol_events.model_dump(exclude_unset=True),
            method="call",
        ),
        "groupers": Node(
            async_task=set_groupers.validate().set_executor("lithops"),
            partial=params.groupers.model_dump(exclude_unset=True),
            method="call",
        ),
        "split_obs": Node(
            async_task=split_groups.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("patrol_events"),
                "groupers": DependsOn("groupers"),
            }
            | params.split_obs.model_dump(exclude_unset=True),
            method="call",
        ),
        "map_layers": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params.map_layers.model_dump(exclude_unset=True),
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_obs"),
            },
        ),
        "ecomaps": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params.ecomaps.model_dump(exclude_unset=True),
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("map_layers"),
            },
        ),
        "ecomaps_persist": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params.ecomaps_persist.model_dump(exclude_unset=True),
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("ecomaps"),
            },
        ),
        "ecomap_widgets": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params.ecomap_widgets.model_dump(exclude_unset=True),
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("ecomaps_persist"),
            },
        ),
        "ecomap_widgets_merged": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("ecomap_widgets"),
            }
            | params.ecomap_widgets_merged.model_dump(exclude_unset=True),
            method="call",
        ),
        "dashboard": Node(
            async_task=gather_dashboard.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("ecomap_widgets_merged"),
                "groupers": DependsOn("groupers"),
            }
            | params.dashboard.model_dump(exclude_unset=True),
            method="call",
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    return results
