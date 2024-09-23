import logging
from dataclasses import dataclass, field
from graphlib import TopologicalSorter
from typing import Any, Literal

from ecoscope_workflows_core.decorators import AsyncTask
from ecoscope_workflows_core.executors import Future, FutureSequence

logger = logging.getLogger(__name__)


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
FuturesDict = dict[str, Future | FutureSequence]
Gathered = Any | list[Any]
GatheredDict = dict[str, Gathered]
GlobalGatheredDict = GatheredDict


def gather_dependencies(
    kwargs: dict[str, Gathered | Dependency],
    futures: FuturesDict,
    global_gathered_dict: GatheredDict,
) -> tuple[GatheredDict, GlobalGatheredDict]:
    gathered_dict = {}
    for k, v in kwargs.items():
        match v:
            case DependsOn():
                if v.node_name in global_gathered_dict:
                    gathered = global_gathered_dict[v.node_name]
                else:
                    gathered = futures[v.node_name].gather()
                    global_gathered_dict[v.node_name] = gathered
            case DependsOnSequence():
                gathered = []
                for x in v:
                    if x.node_name in global_gathered_dict:
                        gathered.append(global_gathered_dict[x.node_name])
                    else:
                        x_gathered = futures[x.node_name].gather()
                        gathered.append(x_gathered)
                        global_gathered_dict[x.node_name] = x_gathered
            case _:
                gathered = v
        gathered_dict[k] = gathered

    return gathered_dict, global_gathered_dict


@dataclass
class Graph:
    dependencies: Dependencies
    nodes: Nodes

    # TODO: __post_init__ to validate that all dependencies are in nodes

    def execute(self) -> dict[str, Any]:
        ts = TopologicalSorter(self.dependencies)
        ts.prepare()
        futures: FuturesDict = {}
        global_gathered_dict: GlobalGatheredDict = {}
        while ts.is_active():
            ready = [name for name in ts.get_ready()]
            for name in sorted(ready):
                logger.info(f"Executing node: '{name}'")
                node = self.nodes[name]
                hydrated_kwargs, global_gathered_dict = gather_dependencies(
                    node.kwargs,
                    futures,
                    global_gathered_dict,
                )
                hydrated_partial, global_gathered_dict = gather_dependencies(
                    node.partial,
                    futures,
                    global_gathered_dict,
                )
                partial = getattr(node.async_task, "partial")(**hydrated_partial)
                callable_method = getattr(partial, node.method)
                future = callable_method(**hydrated_kwargs)
                futures[name] = future
            for name in ready:
                ts.done(name)

        # here, all nodes in ready are terminal nodes
        return {n: futures[n].gather() for n in ready}
