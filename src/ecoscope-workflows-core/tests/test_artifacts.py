from textwrap import dedent

import pytest

from ecoscope_workflows_core.artifacts import PixiToml


@pytest.fixture
def sample_pixitoml():
    return PixiToml.from_text(
        dedent(
            """\
            [project]
            name = "default"
            channels = [
                "file:///tmp/ecoscope-workflows/release/artifacts/",
                "https://repo.prefix.dev/ecoscope-workflows/",
                "conda-forge",
            ]
            platforms = ["linux-64", "linux-aarch64", "osx-arm64"]

            [dependencies]
            ecoscope-workflows-core = { version = "*", channel = "file:///tmp/ecoscope-workflows/release/artifacts/" }

            [feature.test.dependencies]
            pytest = "*"
            [feature.test.tasks]
            test-async-local-mock-io = "python -m pytest tests -k 'async and mock-io'"
            test-sequential-local-mock-io = "python -m pytest tests -k 'sequential and mock-io'"

            [environments]
            default = { solve-group = "default" }
            test = { features = ["test"], solve-group = "default" }
            """
        )
    )


def test_pixitoml_from_text():
    content = dedent(
        """\
        [project]
        name = "example"
        channels = [
            "https://repo.prefix.dev/ecoscope-workflows/",
            "conda-forge",
        ]
        platforms = ["linux-64", "linux-aarch64", "osx-arm64"]

        [dependencies]
        ecoscope-workflows-core = { version = "*", channel = "https://repo.prefix.dev/ecoscope-workflows/" }
        """
    )
    pixitoml = PixiToml.from_text(content)
    assert pixitoml.project.name == "example"


def test_pixitoml_add_dependencies(sample_pixitoml: PixiToml):
    assert sample_pixitoml.model_dump()["dependencies"] == {
        "ecoscope-workflows-core": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        }
    }
    sample_pixitoml.add_dependency(
        name="ecoscope-workflows-ext-ecoscope",
        version="*",
        channel="file:///tmp/ecoscope-workflows/release/artifacts/",
    )
    assert sample_pixitoml.model_dump()["dependencies"] == {
        "ecoscope-workflows-core": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        },
        "ecoscope-workflows-ext-ecoscope": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        },
    }
