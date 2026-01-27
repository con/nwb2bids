import typing

from ._types import Category, DataStandard, Severity

notification_definitions: dict[str, dict[str, typing.Any]] = {}

# BIDS Dataset description
notification_definitions.update(
    {
        "MultipleLicenses": {
            "title": "WARNING: multiple licenses not supported",
            "reason": "DANDI metadata supports multiple licenses, but BIDS only supports one license.",
            "solution": "Manually specify the license in the dataset_description.json file after conversion.",
            "data_standards": [DataStandard.BIDS],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.WARNING,
        },
    }
)

# Session ID
notification_definitions.update(
    {
        "MissingSessionID": {
            "title": "Missing session ID",
            "reason": "A unique ID is required for all individual sessions.",
            "solution": "Specify the `session_id` field of the NWB file object.",
            "field": "nwbfile.session_id",
            "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.CRITICAL,
        },
        "InvalidSessionID": {
            "title": "Invalid session ID",
            "reason": (
                "The session ID contains invalid characters. "
                "BIDS allows only the plus sign to be used as a separator in the subject entity label. "
                "Underscores, dashes, spaces, slashes, and other special characters (including #) are "
                "expressly forbidden."
            ),
            "solution": "Rename the session without using any special characters except for `+`.",
            "examples": [
                "`ses_01` -> `ses+01`",
                "`session #2` -> `session+2`",
                "`id 2 from 9/1/25` -> `id+2+9+1+25`",
            ],
            "field": "nwbfile.session_id",
            "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
            "category": Category.STYLE_SUGGESTION,
            "severity": Severity.ERROR,
        },
    }
)

# Participant/Subject
notification_definitions.update(
    {
        "MissingParticipant": {
            "title": "Missing participant",
            "reason": "BIDS requires a subject to be specified for each NWB file.",
            "solution": "Add a Subject object to each NWB file.",
            "field": "nwbfile.subject",
            "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
            "category": Category.STYLE_SUGGESTION,
            "severity": Severity.CRITICAL,
        },
        "MissingParticipantID": {
            "title": "Missing participant ID",
            "reason": "A unique ID is required for all individual participants.",
            "solution": "Specify the `subject_id` field of the Subject object attached to the NWB file.",
            "field": "nwbfile.subject.subject_id",
            "data_standards": [DataStandard.BIDS, DataStandard.DANDI],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.CRITICAL,
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
        "MissingParticipantSex": {
            "title": "Missing participant sex",
            "reason": "Archives such as DANDI or EMBER require the subject sex to be specified.",
            "solution": (
                "Specify the `sex` field of the Subject object attached to the NWB file as one of four "
                'options: "M" (for male), "F" (for female), "U" (for unknown), or "O" (for other).\n'
                "NOTE: for certain animal species with more specific genetic determinants, such as C elegans, "
                'use "O" (for other) then further specify the subtypes using other custom fields. For example, '
                '`c_elegans_sex="XO"`'
            ),
            "field": "nwbfile.subject.sex",
            "data_standards": [DataStandard.DANDI],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.CRITICAL,
        },
        "InvalidParticipantSexBIDS": {
            "title": "Invalid participant sex (BIDS)",
            "reason": "Participant sex is not one of the allowed patterns by BIDS.",
            "solution": "Rename the subject sex to be one of the accepted values.",
            "examples": ["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            "field": "nwbfile.subject.sex",
            "data_standards": [DataStandard.BIDS],
            "category": Category.STYLE_SUGGESTION,
            "severity": Severity.ERROR,
        },
        "InvalidParticipantSexArchives": {
            "title": "Invalid participant sex (archives)",
            "reason": "Participant sex is not one of the allowed patterns by the common archives.",
            "solution": "Rename the subject sex to be one of the accepted values.",
            "examples": ["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            "field": "nwbfile.subject.sex",
            "data_standards": [DataStandard.DANDI],
            "category": Category.STYLE_SUGGESTION,
            "severity": Severity.ERROR,
        },
        "MissingSpecies": {
            "title": "Missing participant species",
            "reason": "Archives such as DANDI or EMBER require the subject species to be specified.",
            "solution": (
                "Specify the `species` field of the Subject object attached to the NWB file as a Latin binomial, "
                "obolibrary taxonomy link, or NCBI taxonomy reference."
            ),
            "field": "nwbfile.subject.species",
            "data_standards": [DataStandard.DANDI],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.CRITICAL,
        },
        "InvalidSpecies": {
            "title": "Invalid species",
            "reason": "Participant species is not a proper Latin binomial or NCBI Taxonomy id.",
            "solution": (
                "Rename the subject species to a Latin binomial, obolibrary taxonomy link, or "
                "NCBI taxonomy reference."
            ),
            "field": "nwbfile.subject.species",
            "data_standards": [DataStandard.DANDI],
            "category": Category.SCHEMA_INVALIDATION,
            "severity": Severity.ERROR,
        },
        "MultipleNWB:Participant": {
            "title": "NotImplemented: multiple NWB files",
            "reason": (
                "The `Participant` model for `nwb2bids` does not yet support multiple NWB files. "
                "Only the first will be used."
            ),
            "solution": "`nwb2bids` plans to add support for multiple NWB files in the future.",
            "data_standards": [DataStandard.DANDI],
            "category": Category.INTERNAL_ERROR,
            "severity": Severity.ERROR,
        },
    }
)

# NWB fields
notification_definitions.update(
    {
        "MissingDescription": {
            "title": "Missing description",
            "reason": "A basic description of this field is recommended to improve contextual understanding.",
            "solution": "Add a description to the field.",
            "field": "nwbfile.devices.DeviceWithoutDescription",  # TODO: this field should be overridden
            "data_standards": [DataStandard.NWB],
            "category": Category.STYLE_SUGGESTION,
            "severity": Severity.INFO,
        },
    }
)

# DANDI-specific
notification_definitions.update(
    {
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
        "InvalidDandisetMetadata": {
            "title": "INFO: invalid Dandiset metadata",
            "reason": "This Dandiset has invalid metadata.",
            "solution": "Required dataset description fields are inferred from the raw metadata instead.",
            "category": Category.INTERNAL_ERROR,
            "severity": Severity.INFO,
        },
        "MetadataExtractionFailure": {
            "title": "Failed to extract metadata for one or more sessions",
            "reason": "Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
            "solution": "Required dataset description fields are inferred from the raw metadata instead.",
            "category": Category.INTERNAL_ERROR,
            "severity": Severity.ERROR,
        },
    }
)

# Internal
notification_definitions.update(
    {
        "RemoteInitializationFailure": {
            "title": "Failed to initialize converter on remote Dandiset",
            "reason": "An error occurred while executing `DatasetConverter.from_remote_dandiset`.",
            "solution": "Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
            "category": Category.INTERNAL_ERROR,
            "severity": Severity.ERROR,
        },
        "LocalInitializationFailure": {
            "title": "Failed to initialize converter on local NWB files.",
            "reason": "An error occurred while executing `DatasetConverter.from_nwb_paths`.",
            "solution": "Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
            "category": Category.INTERNAL_ERROR,
            "severity": Severity.ERROR,
        },
    }
)
