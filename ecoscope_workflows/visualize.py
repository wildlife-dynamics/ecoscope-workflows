import pydot


def _build_graph(spec: dict) -> pydot.Dot:
    graph = pydot.Dot(spec["name"], graph_type="graph", rankdir="LR")
    for t in spec["tasks"]:
        label = f"{t}|"
        for arg, _ in spec["tasks"][t].items():
            label += f"<{arg}>{arg}|"
        node = pydot.Node(t, shape="record", label=label[:-1])
        graph.add_node(node)
    for t in spec["tasks"]:
        for _, dep in spec["tasks"][t].items():
            edge = pydot.Edge(dep, t, dir="forward", arrowhead="normal")
            graph.add_edge(edge)
    return graph
