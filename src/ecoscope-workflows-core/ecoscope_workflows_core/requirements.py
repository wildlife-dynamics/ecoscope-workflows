from typing import Annotated, Any

from pydantic import Discriminator, Tag as PydanticTag
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator
from rattler import (
    MatchSpec,
    Channel,
    ChannelConfig,
    NamelessMatchSpec,
    Platform,
    Version,
)

from ecoscope_workflows_core._models import _AllowArbitraryTypes


LOCAL_CHANNEL = Channel(
    "ecoscope-workflows-local",
    ChannelConfig(channel_alias="file:///tmp/ecoscope-workflows/release/artifacts/"),
)
RELEASE_CHANNEL = Channel(
    "ecoscope-workflows-release",
    ChannelConfig(channel_alias="https://repo.prefix.dev/ecoscope-workflows"),
)
CHANNELS: list[Channel] = [LOCAL_CHANNEL, RELEASE_CHANNEL, Channel("conda-forge")]
PLATFORMS: list[Platform] = [
    Platform("linux-64"),
    Platform("linux-aarch64"),
    Platform("osx-arm64"),
]


def _channel_from_str(value: str) -> Channel:
    for channel in CHANNELS:
        if channel.name == value:
            return channel
    raise ValueError(f"Unknown channel {value}")


ChannelType = Annotated[
    Channel,
    BeforeValidator(_channel_from_str),
    PlainSerializer(lambda value: value.name),
]


def _platform_from_str(value: str) -> Platform:
    for platform in PLATFORMS:
        if str(platform) == value:
            return platform
    raise ValueError(f"Unknown platform {value}")


PlatformType = Annotated[
    Platform,
    BeforeValidator(_platform_from_str),
    PlainSerializer(lambda value: str(value)),
]


def _namelessmatchspec_from_dict(value: dict) -> NamelessMatchSpec:
    assert "version" in value, f"Expected 'version' key in {value}"
    assert "channel" in value, f"Expected 'channel' key in {value}"
    foo_pkg = "foo"  # placeholder to use from_match_spec constructor
    m = MatchSpec(f"{value['channel']}::{foo_pkg} {value['version']}")
    return NamelessMatchSpec.from_match_spec(m)


def _namelessmatchspec_from_str(value: str) -> NamelessMatchSpec:
    return NamelessMatchSpec(value)


def _parse_namelessmatchspec(value: str | dict) -> NamelessMatchSpec:
    if isinstance(value, str):
        return _namelessmatchspec_from_str(value)
    return _namelessmatchspec_from_dict(value)


def _serialize_namelessmatchspec(value: NamelessMatchSpec) -> dict:
    return {"version": str(value.version), "channel": value.channel}


NamelessMatchSpecType = Annotated[
    NamelessMatchSpec,
    BeforeValidator(_parse_namelessmatchspec),
    PlainSerializer(_serialize_namelessmatchspec),
]


class LongFormMatchSpec(_AllowArbitraryTypes):
    version: Version
    channel: str = "conda-forge"


def _short_versus_long_form(value: Any) -> str:
    if isinstance(value, dict):
        return "long-form-match-spec"
    return "short-form-match-spec"


def _serialize_matchspec(
    value: Version | LongFormMatchSpec,
) -> str | dict:
    match value:
        case Version():
            return str(value)
        case LongFormMatchSpec():
            return value.model_dump()
        case _:
            raise ValueError(f"Unexpected value {value}")


CondaMatchSpec = Annotated[
    Version | Annotated[LongFormMatchSpec, PydanticTag("long-form-match-spec")],
    Discriminator(_short_versus_long_form),
    PlainSerializer(_serialize_matchspec),
]
