import enum
import pathlib

import pydantic


@enum.unique
class Standard(enum.StrEnum):
    """Related standards used by the `nwb2bids` inspections."""

    DANDI_SCHEMA = enum.auto()
    HED = enum.auto()
    NWB = enum.auto()
    BIDS = enum.auto()


@enum.unique
class Category(enum.StrEnum):
    """Types of inspection categories."""

    INTERNAL_ERROR = enum.auto()
    STYLE_SUGGESTION = enum.auto()


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
    source_file_paths: list[pathlib.Path] | None = pydantic.Field(
        description="If known, the paths of all source NWB file(s) where the issue was detected.",
        default=None,
    )
    target_file_paths: list[pathlib.Path] | None = pydantic.Field(
        description=(
            "If known, the target BIDS paths of all file(s) associated with the session where the issue was detected."
        )
    )
    severity: Severity = pydantic.Field(
        description="Quantifier of relative severity. The larger the value, the more important it is.",
    )

    model_config = pydantic.ConfigDict(frozen=True)
