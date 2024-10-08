from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence, TypeVar

from ecoscope_workflows_core.decorators import task
from ecoscope_workflows_core.executors import Future, FutureSequence, LithopsExecutor
from ecoscope_workflows_core.graph import DependsOn, DependsOnSequence, Graph, Node

T = TypeVar("T")


@dataclass(frozen=True)
class PassthroughFuture(Future[T]):
    future: T

    @lru_cache
    def gather(self) -> T:
        return self.future


@dataclass(frozen=True)
class PassthroughFutureSequence(FutureSequence[T]):
    futures: Sequence[PassthroughFuture[T]]

    @lru_cache
    def gather(self) -> Sequence[T]:
        return [f.gather() for f in self.futures]


def test_graph_basic_tasks():
    @task
    def inc(x: int) -> PassthroughFuture[int]:
        return PassthroughFuture(x + 1)

    @task
    def dec(x: int) -> PassthroughFuture[int]:
        return PassthroughFuture(x - 1)

    @task
    def add(x: int, y: int) -> PassthroughFuture[int]:
        return PassthroughFuture(x + y)

    dependencies = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    nodes = {
        "A": Node(inc, {"x": 1}),
        "B": Node(dec, {"x": DependsOn("A")}),
        "C": Node(add, {"x": DependsOn("A"), "y": 1}),
        "D": Node(add, {"x": DependsOn("B"), "y": DependsOn("C")}),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert results == 4


def test_graph_basic_tasks_lithops():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int) -> int:
        return x - 1

    @task
    def add(x: int, y: int) -> int:
        return x + y

    dependencies = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    nodes = {
        "A": Node(inc.set_executor("lithops"), {"x": 1}),
        "B": Node(dec.set_executor("lithops"), {"x": DependsOn("A")}),
        "C": Node(add.set_executor("lithops"), {"x": DependsOn("A"), "y": 1}),
        "D": Node(
            add.set_executor("lithops"), {"x": DependsOn("B"), "y": DependsOn("C")}
        ),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert results == 4


def test_graph_basic_tasks_lithops_same_executor_instance():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int) -> int:
        return x - 1

    @task
    def add(x: int, y: int) -> int:
        return x + y

    le = LithopsExecutor()

    dependencies = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    nodes = {
        "A": Node(inc.set_executor(le), {"x": 1}),
        "B": Node(dec.set_executor(le), {"x": DependsOn("A")}),
        "C": Node(add.set_executor(le), {"x": DependsOn("A"), "y": 1}),
        "D": Node(add.set_executor(le), {"x": DependsOn("B"), "y": DependsOn("C")}),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert results == 4


def test_graph_tasks_lithops_map():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int) -> int:
        return x - 1

    dependencies = {"A": [], "B": [], "C": [], "D": ["A", "B", "C"]}
    nodes = {
        "A": Node(inc.set_executor("lithops"), {"x": 1}),
        "B": Node(inc.set_executor("lithops"), {"x": 2}),
        "C": Node(inc.set_executor("lithops"), {"x": 3}),
        "D": Node(
            dec.set_executor("lithops"),
            method="map",
            kwargs={
                "argnames": ["x"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("A"),
                        DependsOn("C"),
                        DependsOn("B"),
                    ],
                ),
            },
        ),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert set(results) == {1, 2, 3}  # order is not guaranteed


def test_graph_tasks_lithops_map_same_executor_instance():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int) -> int:
        return x - 1

    le = LithopsExecutor()

    dependencies = {"A": [], "B": [], "C": [], "D": ["A", "B", "C"]}
    nodes = {
        "A": Node(inc.set_executor(le), {"x": 1}),
        "B": Node(inc.set_executor(le), {"x": 2}),
        "C": Node(inc.set_executor(le), {"x": 3}),
        "D": Node(
            dec.set_executor(le),
            method="map",
            kwargs={
                "argnames": ["x"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("A"),
                        DependsOn("C"),
                        DependsOn("B"),
                    ],
                ),
            },
        ),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert set(results) == {1, 2, 3}  # order is not guaranteed


def test_graph_tasks_lithops_partial_map():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int, y: int) -> int:
        return x - y - 1

    dependencies = {"A": [], "B": [], "C": [], "D": ["A", "B", "C"]}
    nodes = {
        "A": Node(inc.set_executor("lithops"), {"x": 1}),
        "B": Node(inc.set_executor("lithops"), {"x": 2}),
        "C": Node(inc.set_executor("lithops"), {"x": 3}),
        "D": Node(
            dec.partial(y=1).set_executor("lithops"),
            method="map",
            kwargs={
                "argnames": ["x"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("A"),
                        DependsOn("C"),
                        DependsOn("B"),
                    ],
                ),
            },
        ),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert set(results) == {0, 1, 2}  # order is not guaranteed


def test_graph_tasks_lithops_partial_map_same_executor_instance():
    @task
    def inc(x: int) -> int:
        return x + 1

    @task
    def dec(x: int, y: int) -> int:
        return x - y - 1

    le = LithopsExecutor()

    dependencies = {"A": [], "B": [], "C": [], "D": ["A", "B", "C"]}
    nodes = {
        "A": Node(inc.set_executor(le), {"x": 1}),
        "B": Node(inc.set_executor(le), {"x": 2}),
        "C": Node(inc.set_executor(le), {"x": 3}),
        "D": Node(
            dec.partial(y=1).set_executor(le),
            method="map",
            kwargs={
                "argnames": ["x"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("A"),
                        DependsOn("C"),
                        DependsOn("B"),
                    ],
                ),
            },
        ),
    }
    graph = Graph(dependencies, nodes)
    results = graph.execute()
    assert set(results) == {0, 1, 2}  # order is not guaranteed
