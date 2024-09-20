from pydantic import BaseModel

__all__ = ["_AllowArbitraryTypes"]


class _AllowArbitraryTypes(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)
