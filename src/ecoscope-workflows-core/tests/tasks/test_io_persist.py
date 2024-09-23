import hashlib
import os

from ecoscope_workflows_core.tasks.io import persist_text


def test_persist_text(tmp_path):
    text = "<div>map</div>"
    root_path = str(tmp_path / "test")
    filename = "map.html"
    dst = persist_text(text, root_path, filename)
    with open(dst) as f:
        assert f.read() == text
    assert dst == os.path.join(root_path, filename)


def test_persist_text_generated_filename(tmp_path):
    text = "<div>map</div>"
    root_path = str(tmp_path / "test")
    dst = persist_text(text, root_path)
    with open(dst) as f:
        assert f.read() == text
    expected_filename = hashlib.sha256(text.encode()).hexdigest()[:7] + ".html"
    assert dst == os.path.join(root_path, expected_filename)
