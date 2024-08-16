from dataclasses import dataclass
from functools import lru_cache
from typing import TypeVar
from textwrap import dedent

import yaml

from ecoscope_workflows.compiler import Spec, TaskInstance
from ecoscope_workflows.decorators import task
from ecoscope_workflows.executors import Future, LithopsExecutor
from ecoscope_workflows.graph import DependsOn, Graph, Node

T = TypeVar("T")


@dataclass(frozen=True)
class PassthroughFuture(Future[T]):
    future: T

    @lru_cache
    def gather(self) -> T:
        return self.future


def test_graph_basic():
    def inc(x: int) -> PassthroughFuture[int]:
        return PassthroughFuture(x + 1)

    def dec(x: int) -> PassthroughFuture[int]:
        return PassthroughFuture(x - 1)

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
    assert results == {"D": 4}


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
    assert results == {"D": 4}


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
    assert results == {"D": 4}


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
    assert results == {"D": 4}


def test_graph_from_spec():
    s = dedent(
        """\
        id: map_example
        workflow:
        - name: Get Observations A
          id: obs_a
          task: get_subjectgroup_observations
        - name: Get Observations B
          id: obs_b
          task: get_subjectgroup_observations
        - name: Create Map Layer For Each Group
          id: map_layers
          task: create_map_layer
          map:
            argnames: geodataframe
            argvalues:
              - ${{ workflow.obs_a.return }}
              - ${{ workflow.obs_b.return }}
              - ${{ workflow.obs_c.return }}
        - name: Create EcoMap For Each Group
          id: ecomaps
          task: draw_ecomap
          map:
            argnames: geo_layers
            argvalues: ${{ workflow.map_layers.return }}
        """
    )
    spec = Spec(**yaml.safe_load(s))

    def get_ti_from_id(spec: Spec, id: str) -> TaskInstance:  # TODO: move to spec
        return next(ti for ti in spec.workflow if ti["id"] == id)

    nodes = {
        "obs_a": Node(
            get_ti_from_id(spec.workflow, "obs_a")
            .known_task.function.validate()
            .set_executor(None),
            spec.tasks["get_subjectgroup_observations"].parameters,
        ),
        "obs_b": Node(
            spec.tasks["get_subjectgroup_observations"].validate().set_executor(None),
            spec.tasks["get_subjectgroup_observations"].parameters,
        ),
        "obs_c": Node(
            spec.tasks["get_subjectgroup_observations"].validate().set_executor(None),
            spec.tasks["get_subjectgroup_observations"].parameters,
        ),
        "map_layers": Node(
            spec.tasks["create_map_layer"]
            .validate()
            .partial(**spec.tasks["create_map_layer"].parameters)
            .set_executor(None),
            {
                "argnames": ["geodataframe"],
                "argvalues": [
                    DependsOn("obs_a"),
                    DependsOn("obs_b"),
                    DependsOn("obs_c"),
                ],
            },
        ),
    }
    graph = Graph(  # TODO: Graph.from_spec(spec) ? (or similar)
        dependencies=spec.task_instance_dependencies,
        nodes=nodes,
    )
    results = graph.execute()
    assert results is not None
