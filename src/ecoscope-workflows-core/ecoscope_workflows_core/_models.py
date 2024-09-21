from pydantic import BaseModel

__all__ = [
    "_AllowArbitraryTypes",
    "_ValidateAssignment",
    "_AllowArbitraryAndValidateAssignment",
]


class _AllowArbitraryTypes(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)


class _ValidateAssignment(BaseModel):
    model_config = dict(validate_assignment=True)


class _AllowArbitraryAndValidateAssignment(BaseModel):
    model_config = dict(arbitrary_types_allowed=True, validate_assignment=True)
