import typing

from ._types import Category, DataStandard, Severity

notification_definitions: dict[str, dict[str, typing.Any]] = {
    "MissingParticipantID": {
        "title": "Missing participant ID",
        "reason": "A unique ID is required for all individual participants.",
        "solution": "Specify the `subject_id` field of the Subject object attached to the NWB file.",
        "field": "nwbfile.subject.subject_id",
        "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
        "category": Category.SCHEMA_INVALIDATION,
        "severity": Severity.CRITICAL,
    },
    "DandisetAlreadyBIDS": {
        "title": "Dandiset is already BIDS",
        "reason": (
            "Dandiset is already organized to the BIDS standard. If only a partial conversion is desired, "
            "please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
        ),
        "solution": "Skip the conversion of this Dandiset.",
        "category": Category.INTERNAL_ERROR,
        "severity": Severity.ERROR,
    },
    "InvalidParticipantID": {
        "title": "Invalid participant ID",
        "reason": (
            "The participant ID contains invalid characters. "
            "BIDS allows only the plus sign to be used as a separator in the subject entity label. "
            "Underscores, dashes, spaces, slashes, and other special characters (including #) are "
            "expressly forbidden."
        ),
        "solution": "Rename the subject without using any special characters except for `+`.",
        "examples": [
            "`ab_01` -> `ab+01`",
            "`subject #2` -> `subject+2`",
            "`id 2 from 9/1/25` -> `id+2+9+1+25`",
        ],
        "field": "nwbfile.subject.subject_id",
        "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
        "category": Category.STYLE_SUGGESTION,
        "severity": Severity.ERROR,
    },
}
