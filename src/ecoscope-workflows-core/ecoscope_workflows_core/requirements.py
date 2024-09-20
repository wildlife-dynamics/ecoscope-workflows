from typing import Annotated, Any

from packaging.requirements import SpecifierSet
from packaging.version import Version
from pydantic import Discriminator, Tag as PydanticTag
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator

from ecoscope_workflows_core._models import _AllowArbitraryTypes


def _parse_version_or_specifier(input_str):
    if any(op in input_str for op in ["<", ">", "=", "!", "~"]):
        return SpecifierSet(input_str)
    elif input_str == "*":
        return SpecifierSet()
    else:
        return Version(input_str)


def _serialize_version_or_specset(value: Version | SpecifierSet) -> str:
    match value:
        case Version():
            return str(value)
        case SpecifierSet():
            if not value:
                return "*"
            return str(value)
        case _:
            raise ValueError(f"Unexpected value {value}")


VersionOrSpecSet = Annotated[
    Version | SpecifierSet,
    BeforeValidator(_parse_version_or_specifier),
    PydanticTag("short-form-conda-dep"),
    PlainSerializer(_serialize_version_or_specset),
]


class LongFormCondaDependency(_AllowArbitraryTypes):
    version: VersionOrSpecSet
    channel: str = "conda-forge"


def _short_versus_long_form(value: Any) -> str:
    if isinstance(value, dict):
        return "long-form-conda-dep"
    return "short-form-conda-dep"


def _serialize_conda_dependency(
    value: Version | SpecifierSet | LongFormCondaDependency,
) -> str | dict:
    match value:
        case Version() | SpecifierSet():
            return _serialize_version_or_specset(value)
        case LongFormCondaDependency():
            return value.model_dump()
        case _:
            raise ValueError(f"Unexpected value {value}")


CondaDependency = Annotated[
    VersionOrSpecSet
    | Annotated[LongFormCondaDependency, PydanticTag("long-form-conda-dep")],
    Discriminator(_short_versus_long_form),
    PlainSerializer(_serialize_conda_dependency),
]
