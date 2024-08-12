from typing import Literal, TypeAlias

IndexName: TypeAlias = str
IndexValue: TypeAlias = str
Filter = tuple[IndexName, Literal["="], IndexValue]
CompositeFilter = tuple[Filter, ...]
