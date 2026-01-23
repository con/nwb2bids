import enum
import json
import pathlib

import pydantic
import typing_extensions

from ._definitions import notification_definitions
from ._types import Category, DataStandard, Severity


class Notification(pydantic.BaseModel):
    notification_id: str | None = pydantic.Field(  # TODO: when all are updated, make this required
        description="Unique identifier for the issue.", frozen=True, default=None
    )
    title: str = pydantic.Field(description="Short title of the issue.", frozen=True)
    reason: str = pydantic.Field(description="Detailed description of the issue.", frozen=True)
    solution: str = pydantic.Field(description="Suggestions for how to resolve the issue.", frozen=True)
    examples: list[str] | None = pydantic.Field(
        description="Example solutions to the issue.",
        default=None,
        frozen=True,
    )
    field: str | None = pydantic.Field(
        description=(
            "Best description of the location within the file where the issue was detected "
            "(such as field name, group, etc.)."
        ),
        default=None,
        frozen=True,
    )
    data_standards: list[DataStandard] | None = pydantic.Field(
        description="Data standard(s) related to the issue.", default=None, frozen=True
    )
    source_file_paths: list[pathlib.Path] | list[pydantic.HttpUrl] | None = pydantic.Field(
        description="If known, the paths of all source NWB file(s) where the issue was detected.",
        default=None,
    )
    target_file_paths: list[pathlib.Path] | list[pydantic.HttpUrl] | None = pydantic.Field(
        description=(
            "If known, the target BIDS paths of all file(s) associated with the session where the issue was detected."
        ),
        default=None,
    )
    category: Category = pydantic.Field(description="Type of inspection category.")
    severity: Severity = pydantic.Field(
        description="Quantifier of relative severity. The larger the value, the more important it is.",
    )

    model_config = pydantic.ConfigDict(validate_assignment=True)

    @classmethod
    def from_definition(
        cls,
        notification_id: str,
        source_file_paths: list[pathlib.Path] | list[pydantic.HttpUrl] | None = None,
        target_file_paths: list[pathlib.Path] | list[pydantic.HttpUrl] | None = None,
    ) -> typing_extensions.Self:
        return cls(
            notification_id=notification_id,
            source_file_paths=source_file_paths,
            target_file_paths=target_file_paths,
            **notification_definitions[notification_id],
        )

    # TODO: remove this when/if PyNWB fixes source container for remfile objects
    @pydantic.field_validator("source_file_paths", mode="after")
    def validate_source_file_paths(cls, value: list[str] | None) -> list[str] | None:
        """Remove any paths that contain 'remfile', which NWB source container fields include automatically."""
        if value is None:
            return None
        scrubbed = [path for path in value if "remfile" not in str(path)]
        scrubbed_source_file_paths = None if len(scrubbed) == 0 else scrubbed
        return scrubbed_source_file_paths

    def model_dump(self, **kwargs) -> dict:
        mode = kwargs.pop("mode", "python")
        python_data = super().model_dump(mode="python", **kwargs)

        if mode == "json":
            json_data = json.loads(_CustomJSONEncoder().encode(python_data))
            return json_data

        return python_data


class _CustomJSONEncoder(json.JSONEncoder):
    """
    Required to generate custom desired JSON output when using the Enum fields.

    Without the enum fields,
    """

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        elif isinstance(obj, pydantic.HttpUrl):
            return str(obj)
        elif isinstance(obj, pathlib.Path):
            return str(obj)
        return super().default(obj)
