from textwrap import dedent

from ecoscope_workflows_core.artifacts import PixiToml


def test_PixiToml():
    # TODO: how do we use/register the canonical names for custom channels with py-rattler?
    content = dedent(
        """\
        [project]
        name = "example"
        channels = [
            "ecoscope-workflows-local",
            "ecoscope-workflows-release",
            "conda-forge",
        ]
        platforms = ["linux-64", "linux-aarch64", "osx-arm64"]

        [dependencies]
        ecoscope-workflows-core = { version = "*", channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }
        ecoscope-workflows-ext-ecoscope = {version = "*", channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }
        """
    )
    pixitoml = PixiToml.from_text(content)
    assert pixitoml.project.name == "example"
