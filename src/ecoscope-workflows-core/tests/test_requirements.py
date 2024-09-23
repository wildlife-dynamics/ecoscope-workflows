from ecoscope_workflows_core.requirements import (
    _namelessmatchspec_from_dict,
    _serialize_namelessmatchspec,
)


def test_roundtrip_namelessmatchspec():
    value = {
        "version": ">=0.1.0",
        "channel": "https://repo.prefix.dev/ecoscope-workflows/",
    }
    nms = _namelessmatchspec_from_dict(value)
    assert value == _serialize_namelessmatchspec(nms)
