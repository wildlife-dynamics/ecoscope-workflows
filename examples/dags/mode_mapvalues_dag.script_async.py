import argparse
import os
import yaml

from ecoscope_workflows.graph import DependsOn, Graph, Node

from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("mapvalues_example")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)

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
            partial=params["patrol_events"],
            method="call",
        ),
        "groupers": Node(
            async_task=set_groupers.validate().set_executor("lithops"),
            partial=params["groupers"],
            method="call",
        ),
        "split_obs": Node(
            async_task=split_groups.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("patrol_events"),
                "groupers": DependsOn("groupers"),
            }
            | params["split_obs"],
            method="call",
        ),
        "map_layers": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params["map_layers"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_obs"),
            },
        ),
        "ecomaps": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params["ecomaps"],
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
            | params["ecomaps_persist"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("ecomaps"),
            },
        ),
        "ecomap_widgets": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params["ecomap_widgets"],
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
            | params["ecomap_widgets_merged"],
            method="call",
        ),
        "dashboard": Node(
            async_task=gather_dashboard.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("ecomap_widgets_merged"),
                "groupers": DependsOn("groupers"),
            }
            | params["dashboard"],
            method="call",
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
