from dataclasses import dataclass
from graphlib import TopologicalSorter
from typing import Any, Callable

from ecoscope_workflows.executors import Future, FutureSequence


@dataclass
class DependsOn:
    node_name: str


@dataclass
class Node:
    async_callable: Callable
    params: dict[str, Any | DependsOn]


Dependencies = dict[str, list[str]]  # TODO: `set` instead of `list`
Nodes = dict[str, Node]


@dataclass
class Graph:
    dependencies: Dependencies
    nodes: Nodes

    def execute(self) -> dict[str, Any]:
        ts = TopologicalSorter(self.dependencies)
        ts.prepare()
        futures: dict[str, Future | FutureSequence] = {}
        while ts.is_active():
            ready = [name for name in ts.get_ready()]
            for name in ready:
                node = self.nodes[name]
                hydrated_params = {}
                for k, v in node.params.items():
                    match v:
                        case DependsOn(v.node_name):
                            resolved = futures[v.node_name].gather()
                        case list() if all(isinstance(x, DependsOn) for x in v):
                            resolved = [futures[x.node_name].gather() for x in v]
                        case _:
                            resolved = v
                    hydrated_params[k] = resolved
                future = node.async_callable(**hydrated_params)
                futures[name] = future
            for name in ready:
                ts.done(name)

        # here, all nodes in ready are terminal nodes
        return {n: futures[n].gather() for n in ready}
