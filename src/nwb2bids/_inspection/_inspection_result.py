import enum
import json
import pathlib

import pydantic

from ._json_encoder import CustomJSONEncoder


@enum.unique
class DataStandard(enum.Enum):
    """Related standards used by the `nwb2bids` inspections."""

    DANDI = enum.auto()
    HED = enum.auto()
    NWB = enum.auto()
    BIDS = enum.auto()


@enum.unique
class Category(enum.Enum):
    """Types of inspection categories."""

    STYLE_SUGGESTION = enum.auto()
    SCHEMA_INVALIDATION = enum.auto()
    INTERNAL_ERROR = enum.auto()


@enum.unique
class Severity(enum.IntEnum):
    """
    Quantifier of relative severity (how important it is to resolve) for inspection results.

    The larger the value, the more critical it is.

    If an issue can be categorized in multiple ways, the most severe category should be chosen.
    """

    INFO = enum.auto()  # Not an indication of problem but information of status or confirmation
    HINT = enum.auto()  # Data is valid but could be improved
    WARNING = enum.auto()  # Data is not recognized as valid. Changes are needed to ensure validity
    ERROR = enum.auto()  # Data is recognized as invalid
    CRITICAL = enum.auto()  # A serious invalidity in data


class InspectionResult(pydantic.BaseModel):
    title: str = pydantic.Field(description="Short title of the issue.")
    reason: str = pydantic.Field(description="Detailed description of the issue and suggestions for how to resolve it.")
    solution: str = pydantic.Field(
        description="Detailed description of the issue and suggestions for how to resolve it."
    )
    examples: list[str] | None = pydantic.Field(
        description="Detailed description of the issue and suggestions for how to resolve it.", default=None
    )
    field: str | None = pydantic.Field(
        description=(
            "Best description of the location within the file where the issue was detected "
            "(such as field name, group, etc.)."
        ),
        default=None,
    )
    source_file_paths: set[pathlib.Path | pydantic.HttpUrl] | None = pydantic.Field(
        description="If known, the paths of all source NWB file(s) where the issue was detected.",
        default=None,
    )
    target_file_paths: set[pathlib.Path | pydantic.HttpUrl] | None = pydantic.Field(
        description=(
            "If known, the target BIDS paths of all file(s) associated with the session where the issue was detected."
        ),
        default=None,
    )
    data_standards: list[DataStandard] | None = pydantic.Field(
        description="Data standard(s) related to the issue.", default=None
    )
    category: Category = pydantic.Field(description="Type of inspection category.")
    severity: Severity = pydantic.Field(
        description="Quantifier of relative severity. The larger the value, the more important it is.",
    )

    # TODO: remove this when/if PyNWB fixes source container for remfile objects
    @pydantic.field_validator(field="source_file_paths", mode="after")
    def validate_source_file_paths(
        cls, value: set[pathlib.Path | pydantic.HttpUrl] | None
    ) -> set[pathlib.Path | pydantic.HttpUrl] | None:
        """Remove any paths that contain 'remfile', which NWB source container fields include automatically."""
        if value is None:
            return None
        scrubbed = [path for path in value if "remfile" not in str(path)]
        scrubbed_source_file_paths = None if len(scrubbed) == 0 else scrubbed
        return scrubbed_source_file_paths

    # TODO: remove when StrEnum is integrated (3.11 minimum)
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        json_data = json.loads(CustomJSONEncoder().encode(data))
        return json_data
