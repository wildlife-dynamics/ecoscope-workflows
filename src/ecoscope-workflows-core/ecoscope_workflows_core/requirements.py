from typing import Annotated

from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator
from rattler import (
    MatchSpec,
    Channel,
    ChannelConfig,
    NamelessMatchSpec as _NamelessMatchSpec,
    Platform,
)

LOCAL_CHANNEL = Channel(
    "artifacts",
    ChannelConfig(channel_alias="file:///tmp/ecoscope-workflows/release/"),
)
RELEASE_CHANNEL = Channel(
    "ecoscope-workflows",
    ChannelConfig(channel_alias="https://repo.prefix.dev/"),
)
CHANNELS: list[Channel] = [LOCAL_CHANNEL, RELEASE_CHANNEL, Channel("conda-forge")]
PLATFORMS: list[Platform] = [
    Platform("linux-64"),
    Platform("linux-aarch64"),
    Platform("osx-arm64"),
]


# FIXME: workaround for https://github.com/conda/rattler/issues/869
# this override can be removed once the issue is resolved.
class NamelessMatchSpec(_NamelessMatchSpec):
    @property
    def channel(self):
        if (channel := self._nameless_match_spec.channel) is not None:
            return next(c for c in CHANNELS if c.name == channel.name)
        return None


def _channel_from_str(value: str) -> Channel:
    for channel in CHANNELS:
        # TODO(cisaacstern): base_url equality check can be stymied by presence or absense
        # of trailing slash on the base_url. Sanitize the base_url to prevent this issue.
        if channel.name == value or channel.base_url == value:
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


def _namelessmatchspec_from_dict(value: dict[str, str]) -> NamelessMatchSpec:
    assert "version" in value, f"Expected 'version' key in {value}"
    assert "channel" in value, f"Expected 'channel' key in {value}"
    # FIXME: workaround for https://github.com/conda/rattler/issues/869
    # this conditional block can be removed once the issue is resolved.
    match value["channel"]:
        case _ if value["channel"] in [
            c.base_url for c in (LOCAL_CHANNEL, RELEASE_CHANNEL)
        ]:
            channel = next(c.name for c in CHANNELS if c.base_url == value["channel"])
        case str("conda-forge"):
            channel = value["channel"]
        case _:
            raise ValueError(f"Unknown channel {value['channel']}")
    foo_pkg = "foo"  # placeholder to use from_match_spec constructor
    m = MatchSpec(f"{channel}::{foo_pkg} {value['version']}")
    # FIXME: this type error is a side effect of the override for NamelessMatchSpec
    # and can be removed once the issue linked there is resolved.
    return NamelessMatchSpec.from_match_spec(m)  # type: ignore[return-value]


def _namelessmatchspec_from_str(value: str) -> NamelessMatchSpec:
    return NamelessMatchSpec(value)


def _parse_namelessmatchspec(value: str | dict) -> NamelessMatchSpec:
    if isinstance(value, str):
        return _namelessmatchspec_from_str(value)
    return _namelessmatchspec_from_dict(value)


def _serialize_namelessmatchspec(value: NamelessMatchSpec) -> dict:
    # FIXME: workaround for https://github.com/conda/rattler/issues/869
    # this conditional block can be removed once the issue is resolved.
    match value.channel:
        case None:
            channel = None
        case c if c.base_url in [
            channel.base_url for channel in (LOCAL_CHANNEL, RELEASE_CHANNEL)
        ]:
            channel = next(
                c.base_url for c in CHANNELS if c.base_url == value.channel.base_url
            )
        case str("conda-forge"):
            channel = c
        case _:
            raise ValueError(f"Unknown channel {value.channel}")
    return {"version": str(value.version), "channel": channel}


NamelessMatchSpecType = Annotated[
    NamelessMatchSpec,
    BeforeValidator(_parse_namelessmatchspec),
    PlainSerializer(_serialize_namelessmatchspec),
]
