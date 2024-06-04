import pydot


def _build_graph(spec: dict) -> pydot.Dot:
    graph = pydot.Dot(spec["name"], graph_type="graph", rankdir="LR")
    for t in spec["tasks"]:
        label = (
            "<<table border='1' cellspacing='0'>"
            f"<tr><td port='{t}' border='1' bgcolor='grey'>{t}</td></tr>"
        )
        for arg, _ in spec["tasks"][t].items():
            label += f"<tr><td port='{arg}' border='1'>{arg}</td></tr>"
        label += "<tr><td port='return' border='1'><i>return</i></td></tr>" "</table>>"
        node = pydot.Node(t, shape="none", label=label)
        graph.add_node(node)
    for t in spec["tasks"]:
        for arg, dep in spec["tasks"][t].items():
            edge = pydot.Edge(
                f"{dep}:return", f"{t}:{arg}", dir="forward", arrowhead="normal"
            )
            graph.add_edge(edge)
    return graph


def write_png(spec: dict, outpath: str) -> None:
    graph: pydot.Dot = _build_graph(spec)
    graph.write(path=outpath, format="png")
