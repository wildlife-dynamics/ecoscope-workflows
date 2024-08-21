import argparse
import os
import yaml

from ecoscope_workflows.executors import LithopsExecutor
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

    le = LithopsExecutor()

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
            async_callable=(
                get_patrol_events.validate()
                .partial(**params["patrol_events"])
                .set_executor(le)
                .call
            ),
        ),
        "groupers": Node(
            async_callable=(
                set_groupers.validate()
                .partial(**params["groupers"])
                .set_executor(le)
                .call
            ),
        ),
        "split_obs": Node(
            async_callable=(
                split_groups.validate()
                .partial(df=patrol_events, groupers=groupers, **params["split_obs"])
                .set_executor(le)
                .call
            ),
        ),
        "map_layers": Node(
            async_callable=(
                create_map_layer.validate()
                .partial(**params["map_layers"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_obs"),
            },
        ),
        "ecomaps": Node(
            async_callable=(
                draw_ecomap.validate()
                .partial(**params["ecomaps"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("map_layers"),
            },
        ),
        "ecomaps_persist": Node(
            async_callable=(
                persist_text.validate()
                .partial(
                    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                    **params["ecomaps_persist"],
                )
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["text"],
                "argvalues": DependsOn("ecomaps"),
            },
        ),
        "ecomap_widgets": Node(
            async_callable=(
                create_map_widget_single_view.validate()
                .partial(**params["ecomap_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("ecomaps_persist"),
            },
        ),
        "ecomap_widgets_merged": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(widgets=ecomap_widgets, **params["ecomap_widgets_merged"])
                .set_executor(le)
                .call
            ),
        ),
        "dashboard": Node(
            async_callable=(
                gather_dashboard.validate()
                .partial(
                    widgets=ecomap_widgets_merged,
                    groupers=groupers,
                    **params["dashboard"],
                )
                .set_executor(le)
                .call
            ),
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
