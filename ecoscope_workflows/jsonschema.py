from inspect import signature
from typing import get_args

from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema


# Workaround for https://github.com/pydantic/pydantic/issues/9404
class SurfacesDescriptionSchema(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        if "function" in schema and "properties" in json_schema:
            for p in json_schema["properties"]:
                annotation_args = get_args(signature(schema["function"]).parameters[p].annotation)
                if any([isinstance(arg, FieldInfo) for arg in annotation_args]):
                    Field: FieldInfo = [arg for arg in annotation_args if isinstance(arg, FieldInfo)][0]
                    if Field.description:
                        json_schema["properties"][p]["description"] = Field.description
        return json_schema
