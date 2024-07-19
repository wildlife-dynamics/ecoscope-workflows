import os

from ecoscope_workflows.serde import persist_text


def test_persist_text(tmp_path):
    text = "hello world"
    root_path = str(tmp_path / "test")
    path = persist_text(text, root_path)
    with open(path) as f:
        assert f.read() == text
    assert path == os.path.join(root_path, "map.html")
