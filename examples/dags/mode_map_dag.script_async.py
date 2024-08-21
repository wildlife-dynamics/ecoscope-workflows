import argparse
import os
import yaml

from ecoscope_workflows.executors import LithopsExecutor
from ecoscope_workflows.graph import DependsOn, DependsOnSequence, Graph, Node

from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.results import create_map_layer
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

    le = LithopsExecutor()

    dependencies = {
        "obs_a": [],
        "obs_b": [],
        "obs_c": [],
        "map_layers": ["obs_a", "obs_b", "obs_c"],
        "ecomaps": ["map_layers"],
        "td_ecomap_html_url": ["ecomaps"],
    }

    nodes = {
        "obs_a": Node(
            async_task=get_subjectgroup_observations.validate().set_executor(le),
            partial=params["obs_a"],
            method="call",
        ),
        "obs_b": Node(
            async_task=get_subjectgroup_observations.validate().set_executor(le),
            partial=params["obs_b"],
            method="call",
        ),
        "obs_c": Node(
            async_task=get_subjectgroup_observations.validate().set_executor(le),
            partial=params["obs_c"],
            method="call",
        ),
        "map_layers": Node(
            async_task=create_map_layer.validate().set_executor(le),
            partial=params["map_layers"],
            method="map",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("obs_a"),
                        DependsOn("obs_b"),
                        DependsOn("obs_c"),
                    ],
                ),
            },
        ),
        "ecomaps": Node(
            async_task=draw_ecomap.validate().set_executor(le),
            partial=params["ecomaps"],
            method="map",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("map_layers"),
            },
        ),
        "td_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor(le),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["td_ecomap_html_url"],
            method="map",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("ecomaps"),
            },
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
