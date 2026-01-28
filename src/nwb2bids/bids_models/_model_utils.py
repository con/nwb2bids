import collections
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


def _build_json_sidecar(models: typing.Sequence[pydantic.BaseModel]) -> dict[str, dict[str, typing.Any]]:
    """Build a JSON sidecar dictionary from the provided models."""
    present_non_additional_fields = _get_present_fields(models=models)

    reference_model = list(models)[0]
    json_content: dict[str, dict[str, typing.Any]] = collections.defaultdict(dict)
    for field in present_non_additional_fields:
        if title := getattr(reference_model.model_fields[field], "title"):
            json_content[field]["LongName"] = title
        if description := getattr(reference_model.model_fields[field], "description"):
            json_content[field]["Description"] = description

    return json_content
