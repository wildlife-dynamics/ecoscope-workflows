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

    def __post_init__(self):
        self._results: dict[str, Any] = {}

    def execute(self) -> dict[str, Any]:
        ts = TopologicalSorter(self.dependencies)
        ts.prepare()
        while ts.is_active():
            ready = [name for name in ts.get_ready()]
            futures: dict[str, Future | FutureSequence] = {}
            for name in ready:
                node = self.nodes[name]
                hydrated_params = {}
                for k, v in node.params.items():
                    if isinstance(v, DependsOn):
                        v = self._results[v.node_name]
                    hydrated_params[k] = v
                future = node.async_callable(**hydrated_params)
                futures[name] = future
            for name in ready:
                self._results[name] = futures[name].gather()
                ts.done(name)

        return {k: self._results[k] for k in ready}