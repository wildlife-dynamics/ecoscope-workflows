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
PlatformType = Annotated[
    Platform,
    BeforeValidator(lambda value: Platform(value)),
    PlainSerializer(lambda value: value.name),
]


def _namelessmatchspec_from_dict(value: dict) -> NamelessMatchSpec:
    assert "version" in value, f"Expected 'version' key in {value}"
    assert "channel" in value, f"Expected 'channel' key in {value}"
    foo_pkg = "foo"  # placeholder to use from_match_spec constructor
    m = MatchSpec(f"{value['channel']}::{foo_pkg} {value['version']}")
    return NamelessMatchSpec.from_match_spec(m)


def _namelessmatchspec_to_dict(value: NamelessMatchSpec) -> dict:
    return {"version": str(value.version), "channel": value.channel}


NamelessMatchSpecType = Annotated[
    NamelessMatchSpec,
    BeforeValidator(_namelessmatchspec_from_dict),
    PlainSerializer(_namelessmatchspec_to_dict),
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
