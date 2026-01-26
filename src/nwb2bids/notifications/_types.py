import enum


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
class Severity(enum.Enum):
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
