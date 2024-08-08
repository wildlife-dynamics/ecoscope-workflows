from inspect import signature
from typing import Any, get_args

from pydantic import BaseModel, model_serializer
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema


# Workaround for https://github.com/pydantic/pydantic/issues/9404
class SurfacesDescriptionSchema(GenerateJsonSchema):
    def generate(self, schema, mode="validation"):
        json_schema = super().generate(schema, mode=mode)
        if "function" in schema and "properties" in json_schema:
            for p in json_schema["properties"]:
                annotation_args = get_args(
                    signature(schema["function"]).parameters[p].annotation
                )
                if any([isinstance(arg, FieldInfo) for arg in annotation_args]):
                    Field: FieldInfo = [
                        arg for arg in annotation_args if isinstance(arg, FieldInfo)
                    ][0]
                    if Field.description:
                        json_schema["properties"][p]["description"] = Field.description
        return json_schema


class RJSFFilterProperty(BaseModel):
    """Model representing the properties of a React JSON Schema Form filter.
    This model is used to generate the `properties` field for a filter schema in a dashboard.

    Args:
        _type: The type of the filter property.
        _enum: The possible values for the filter property.
        _enumNames: The human-readable names for the possible values.
        _default: The default value for the filter property
    """

    type: str
    enum: list[str]
    enumNames: list[str]
    default: str


class RJSFFilterUiSchema(BaseModel):
    """Model representing the UI schema of a React JSON Schema Form filter.
    This model is used to generate the `uiSchema` field for a filter schema in a dashboard.

    Args:
        title: The title of the filter.
        help: The help text for the filter.
    """

    title: str
    help: str | None = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {"ui:title": self.title} | ({"ui:help": self.help} if self.help else {})


class RJSFFilter(BaseModel):
    """Model representing a React JSON Schema Form filter."""

    property: RJSFFilterProperty
    uiSchema: RJSFFilterUiSchema


class ReactJSONSchemaFormFilters(BaseModel):
    options: dict[str, RJSFFilter]

    @property
    def _schema(self):
        return {
            "type": "object",
            "properties": {
                opt: rjsf.property.model_dump() for opt, rjsf in self.options.items()
            },
            "uiSchema": {
                opt: rjsf.uiSchema.model_dump() for opt, rjsf in self.options.items()
            },
        }

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        return {"schema": self._schema}
