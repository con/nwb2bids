import enum
import pathlib

import pydantic


class InspectionLevel(enum.Enum):
    """
    Quantifier of relative severity (how important it is to resolve).

    The larger the value, the more critical it is.

    If an issue can be categorized in multiple ways, the most severe category should be chosen.
    """

    SUGGESTION = 0  # Only mild nudges in the right direction
    INVALID_ARCHIVE_VALUE = 1  # A value is present but is invalid according to common archive rules
    MISSING_ARCHIVE_FIELD = 2  # Required for sharing on public archives
    MISSING_ARCHIVE_ENTITY = 3  # Required for sharing on public archives
    INVALID_BIDS_VALUE = 4  # A value is present but is invalid according to BIDS rules
    MISSING_BIDS_FIELD = 5  # A field required for BIDS compliance
    MISSING_BIDS_ENTITY = 6  # An entity required for BIDS compliance
    NOT_IMPLEMENTED = 7  # A planned but not implemented feature for metadata extraction or file conversion
    ERROR = 8  # An actual problem occurred somewhere in the conversion process


class InspectionMessage(pydantic.BaseModel):
    title: str = pydantic.Field(description="Short title of the issue.")
    reason: str = pydantic.Field(description="Detailed description of the issue and suggestions for how to resolve it.")
    solution: str = pydantic.Field(
        description="Detailed description of the issue and suggestions for how to resolve it."
    )
    examples: list[str] | None = pydantic.Field(
        description="Detailed description of the issue and suggestions for how to resolve it.", default=None
    )
    location_in_file: str | None = pydantic.Field(
        description=(
            "Best description of the location within the file where the issue was detected "
            "(such as field name, group, etc.)."
        ),
        default=None,
    )
    file_paths: list[pathlib.Path] | None = pydantic.Field(
        description="If known, the paths of all files associated with the session where the issue was detected.",
        default=None,
    )
    level: InspectionLevel = pydantic.Field(
        description=(
            "Quantifier of relative severity (how important it is to resolve). "
            "The larger the value, the more critical it is."
        ),
    )

    model_config = pydantic.ConfigDict(frozen=True)
