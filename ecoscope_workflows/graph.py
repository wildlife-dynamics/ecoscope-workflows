from dataclasses import dataclass, field
from graphlib import TopologicalSorter
from typing import Any, Literal

from ecoscope_workflows.decorators import AsyncTask
from ecoscope_workflows.executors import Future, FutureSequence


@dataclass
class DependsOn:
    node_name: str


class DependsOnSequence(list[DependsOn]):
    pass


Dependency = DependsOn | DependsOnSequence


@dataclass
class Node:
    async_task: AsyncTask
    partial: dict[str, Any | Dependency] = field(default_factory=dict)
    method: Literal["call", "map", "mapvalues"] = "call"
    kwargs: dict[str, Any | Dependency] = field(default_factory=dict)


Dependencies = dict[str, list[str]]  # TODO: `set` instead of `list`
Nodes = dict[str, Node]


@dataclass
class Graph:
    dependencies: Dependencies
    nodes: Nodes

    # TODO: __post_init__ to validate that all dependencies are in nodes

    def execute(self) -> dict[str, Any]:
        ts = TopologicalSorter(self.dependencies)
        ts.prepare()
        futures: dict[str, Future | FutureSequence] = {}
        while ts.is_active():
            ready = [name for name in ts.get_ready()]
            for name in ready:
                node = self.nodes[name]
                hydrated_kwargs = {}
                for k, v in node.kwargs.items():
                    match v:
                        case DependsOn():
                            resolved = futures[v.node_name].gather()
                        case DependsOnSequence():
                            resolved = [futures[x.node_name].gather() for x in v]
                        case _:
                            resolved = v
                    hydrated_kwargs[k] = resolved
                # TODO: hydrate dependencies in node.partial
                partial = getattr(node.async_task, "partial")(**node.partial)
                callable_method = getattr(partial, node.method)
                future = callable_method(**hydrated_kwargs)
                futures[name] = future
            for name in ready:
                ts.done(name)

        # here, all nodes in ready are terminal nodes
        return {n: futures[n].gather() for n in ready}
