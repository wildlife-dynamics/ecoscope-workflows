from pydantic import BaseModel, ConfigDict

__all__ = [
    "_AllowArbitraryTypes",
    "_AllowArbitraryAndForbidExtra",
    "_AllowArbitraryAndValidateAssignment",
    "_ForbidExtra",
    "_ValidateAssignment",
]


class _AllowArbitraryTypes(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class _AllowArbitraryAndValidateAssignment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True)


class _AllowArbitraryAndForbidExtra(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")


class _ForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _ValidateAssignment(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
