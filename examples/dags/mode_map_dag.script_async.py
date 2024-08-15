import argparse
import os
from dataclasses import dataclass
from typing import Any, Callable

import yaml

from ecoscope_workflows.executors import LithopsExecutor
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

    @dataclass
    class Node:
        callable: Callable
        params: dict[str, Any]

    @dataclass
    class NodeResult:
        result: Any

    node_results = {
        "obs_a": NodeResult(
            get_subjectgroup_observations.validate()
            .set_executor(le)
            .call(**params["obs_a"]),
        ),
        "obs_b": NodeResult(
            get_subjectgroup_observations.validate()
            .set_executor(le)
            .call(**params["obs_b"]),
        ),
        "obs_c": NodeResult(
            get_subjectgroup_observations.validate()
            .set_executor(le)
            .call(**params["obs_c"]),
        ),
    }
    nodes = {
        "obs_a": Node(
            get_subjectgroup_observations.validate().set_executor(le),
            params["obs_a"],
        ),
        "obs_b": Node(
            get_subjectgroup_observations.validate().set_executor(le),
            params["obs_b"],
        ),
        "obs_c": Node(
            get_subjectgroup_observations.validate().set_executor(le),
            params["obs_c"],
        ),
        "map_layers": Node(
            create_map_layer.validate()
            .partial(**params["map_layers"])
            .set_executor(le),
            {"argnames": ["geodataframe"], "argvalues": [obs_a, obs_b, obs_c]},
        ),
    }

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

    print(td_ecomap_html_url)
