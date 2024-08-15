from dataclasses import dataclass
from typing import TypeVar

from ecoscope_workflows.executors import Future
from ecoscope_workflows.graph import DependsOn, Graph, Node

T = TypeVar("T")


@dataclass
class PassthroughFuture(Future[T]):
    future: T

    def gather(self) -> T:
        return self.future


def inc(x: int) -> PassthroughFuture[int]:
    return PassthroughFuture(x + 1)


def dec(x: int) -> PassthroughFuture[int]:
    return PassthroughFuture(x - 1)


def add(x: int, y: int) -> PassthroughFuture[int]:
    return PassthroughFuture(x + y)


def test_graph_basic():
    dependencies = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    nodes = {
        "A": Node(inc, {"x": 1}),
        "B": Node(dec, {"x": DependsOn("A")}),
        "C": Node(add, {"x": DependsOn("A"), "y": 1}),
        "D": Node(add, {"x": DependsOn("B"), "y": DependsOn("C")}),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert results == {"D": 4}
