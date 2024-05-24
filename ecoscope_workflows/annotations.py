from typing import Annotated, Any, TypeVar, get_origin

import pandera as pa
from pydantic_core import core_schema as cs
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue, WithJsonSchema


class JsonSerializableDataFrameModel(pa.DataFrameModel):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return cls.to_json_schema()


DataFrameSchema = TypeVar("DataFrameSchema", bound=JsonSerializableDataFrameModel)

DataFrame = Annotated[
    pa.typing.DataFrame[DataFrameSchema],
    # pa.typing.DataFrame is very hard to meaningfully serialize to JSON. Pandera itself
    # does not yet support this, see: https://github.com/unionai-oss/pandera/issues/421.
    # The "ideal" workaround I think involves overriding `__get_pydantic_json_schema__`,
    # as worked for `JsonSerializableDataFrameModel` above, however the meaningful data
    # we would want to access within that classmethod is the subscripted `DataframeSchema`
    # type passed by the user. This *is* accessible outside classmethods (in the context
    # in which the subscription happens) with `typing.get_args`. However, that does not work
    # on the `cls` object we have in the classmethod. It *feels* like this SO post somehow
    # points towards a solution: https://stackoverflow.com/a/65064882, but I really struggled
    # to make it work. So in the interim, we will just always use the generic schema declared
    # below, which will not contain any schema-specific information. This *will not* affect
    # validation behavior, only JSON Schema generation.
    WithJsonSchema({"type": "ecoscope.distributed.types.DataFrame"}),
]


class AnyGeoDataFrameSchema(JsonSerializableDataFrameModel):
    # see note in tasks/time_density re: geometry typing
    geometry: pa.typing.Series[Any] = pa.Field()


AnyGeoDataFrame = DataFrame[AnyGeoDataFrameSchema]


def is_subscripted_pandera_dataframe(obj):
    if hasattr(obj, "__origin__") and hasattr(obj, "__args__"):
        if get_origin(obj) == pa.typing.DataFrame:
            return True
    return False
