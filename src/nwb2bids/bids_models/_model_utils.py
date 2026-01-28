import typing

import pydantic
import pydantic_core


def _get_present_fields(models: typing.Sequence[pydantic.BaseModel]) -> set[str]:
    """Return a set of field names that are present or required in the model."""
    present_non_additional_fields = {
        field
        for model in models
        for field, value in model.model_dump().items()
        if field in model.model_fields
        and (
            value is not None
            or model.model_fields.get(field, pydantic.fields.FieldInfo()).default is pydantic_core.PydanticUndefined
        )
    }
    return present_non_additional_fields
