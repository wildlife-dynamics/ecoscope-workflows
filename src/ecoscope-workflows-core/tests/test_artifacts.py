from textwrap import dedent

from ecoscope_workflows_core.artifacts import PixiToml, _default_pixi_toml


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


def test_pixitoml_default_factory():
    expected = PixiToml.from_text(
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
    ).model_dump()
    actual = _default_pixi_toml().model_dump()
    for key, value in actual.items():
        assert expected[key] == value


def test_pixitoml_add_dependencies():
    default: PixiToml = _default_pixi_toml()
    assert default.model_dump()["dependencies"] == {
        "ecoscope-workflows-core": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        }
    }
    default.add_dependency(
        name="ecoscope-workflows-ext-ecoscope",
        version="*",
        channel="file:///tmp/ecoscope-workflows/release/artifacts/",
    )
    assert default.model_dump()["dependencies"] == {
        "ecoscope-workflows-core": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        },
        "ecoscope-workflows-ext-ecoscope": {
            "version": "*",
            "channel": "file:///tmp/ecoscope-workflows/release/artifacts/",
        },
    }
