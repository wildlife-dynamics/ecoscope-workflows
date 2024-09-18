try:
    from pydot import Dot, Node, Edge  # type: ignore[import-untyped]
except ImportError:
    raise ImportError(
        "To use this module, you will need to install visualization dependencies "
        "with 'pip install \".[visualize]\"'."
    )

from ecoscope_workflows.compiler import Spec


def _build_graph(spec: Spec) -> Dot:
    graph = Dot(spec.id, graph_type="graph", rankdir="LR")
    for t in spec.workflow:
        label = (
            "<<table border='1' cellspacing='0'>"
            f"<tr><td port='{t.id}' border='1' bgcolor='grey'>{t.id}</td></tr>"
        )
        for arg in t.all_dependencies_dict:
            label += f"<tr><td port='{arg}' border='1'>{arg}</td></tr>"
        label += "<tr><td port='return' border='1'><i>return</i></td></tr>" "</table>>"
        node = Node(t.id, shape="none", label=label)
        graph.add_node(node)
    for t in spec.workflow:
        for arg, dep in t.all_dependencies_dict.items():
            for d in dep:
                edge = Edge(
                    f"{d}:return", f"{t.id}:{arg}", dir="forward", arrowhead="normal"
                )
                graph.add_edge(edge)
    return graph


def write_png(spec: Spec, outpath: str) -> None:
    graph: Dot = _build_graph(spec)
    graph.write(path=outpath, format="png")
