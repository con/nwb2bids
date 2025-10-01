import typing

import pydantic

from .._inspection._inspection_result import Category, InspectionResult, Severity
from ..bids_models import DatasetDescription
from ..bids_models._model_globals import _BIDS_RRID


def get_bids_dataset_description(dandiset) -> tuple[DatasetDescription | None, list[InspectionResult]]:
    valid_or_raw: typing.Literal["raw", "valid"] = "valid"
    try:
        metadata = dandiset.get_metadata()
    except pydantic.ValidationError:
        raw_metadata = dandiset.get_raw_metadata()
        valid_or_raw = "raw"

    messages = []
    if valid_or_raw == "valid":
        dataset_description, internal_messages = _get_dataset_description_from_valid_dandiset_metadata(
            metadata=metadata
        )
        messages.extend(internal_messages)
    else:
        dataset_description, internal_messages = _get_dataset_description_from_invalid_dandiset_metadata(
            raw_metadata=raw_metadata
        )
        messages.extend(internal_messages)

        message = InspectionResult(
            title="INFO: invalid Dandiset metadata",
            reason="This Dandiset has invalid metadata.",
            solution="Required dataset description fields are inferred from the raw metadata instead.",
            category=Category.INTERNAL_ERROR,
            severity=Severity.INFO,
        )
        messages.append(message)

    return dataset_description, messages


def _get_dataset_description_from_valid_dandiset_metadata(
    metadata: typing.Any,
) -> tuple[DatasetDescription | None, list[InspectionResult]]:
    dataset_description_kwargs = dict()

    dataset_description_kwargs["Name"] = metadata.name
    dataset_description_kwargs["BIDSVersion"] = "1.10"

    messages = []
    if any(data_standard.identifier == _BIDS_RRID for data_standard in metadata.assetsSummary.dataStandard):
        reason = (
            "Dandiset is already organized to the BIDS standard. If only a partial conversion is desired, "
            "please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
        )
        message = InspectionResult(
            title="Dandiset is already BIDS",
            reason=reason,
            solution="Skip the conversion of this Dandiset.",
            category=Category.INTERNAL_ERROR,
            severity=Severity.ERROR,
        )
        messages.append(message)
        return None, messages

    if metadata.description is not None:
        dataset_description_kwargs["Description"] = metadata.description
    if metadata.contributor is not None:
        dataset_description_kwargs["Authors"] = [
            contributor.name
            for contributor in metadata.contributor
            for role in contributor.roleName
            if role.value == "dcite:Author"
        ]
    if metadata.license is not None:
        dataset_description_kwargs["License"] = metadata.license[0].value.split(":")[1]

    dataset_description = DatasetDescription(**dataset_description_kwargs)
    return dataset_description, messages


def _get_dataset_description_from_invalid_dandiset_metadata(
    raw_metadata: typing.Any,
) -> tuple[DatasetDescription | None, list[InspectionResult]]:
    dataset_description_kwargs = dict()

    dandiset_identifier = raw_metadata.get("identifier", "??????")
    dataset_description_kwargs["Name"] = raw_metadata.get("name", f"DANDI Archive Dandiset {dandiset_identifier}")
    dataset_description_kwargs["BIDSVersion"] = "1.10"

    assets_summary = raw_metadata.get("assetsSummary", dict())
    data_standards = assets_summary.get("dataStandard", [])

    messages = []
    if any(data_standard.get("identifier", "") == _BIDS_RRID for data_standard in data_standards):
        reason = (
            "Dandiset is already organized to the BIDS standard. If only a partial conversion is desired, "
            "please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
        )
        message = InspectionResult(
            title="Dandiset is already BIDS",
            reason=reason,
            solution="Skip the conversion of this Dandiset.",
            category=Category.INTERNAL_ERROR,
            severity=Severity.ERROR,
        )
        messages.append(message)
        return None, messages

    dandiset_description = raw_metadata.get("description", None)
    if dandiset_description is not None:
        dataset_description_kwargs["Description"] = dandiset_description

    bids_authors = []
    dandiset_contributors = raw_metadata.get("contributors", [])
    for contributor in dandiset_contributors:
        contributor_name = contributor.get("name", None)
        authorship = [role_value == "dcite:Author" for role_value in contributor.get("roleName", [])]
        if contributor_name is not None and any(authorship):
            bids_authors.append(contributor_name)

    if any(bids_authors):
        dataset_description_kwargs["Authors"] = bids_authors

    license = raw_metadata.get("license", [])
    if len(license) > 0:
        if len(license) == 1:
            dataset_description_kwargs["License"] = license[0].split(":")[-1]
        else:
            message = InspectionResult(
                title="WARNING: multiple licenses not supported",
                reason="DANDI metadata supports multiple licenses, but BIDS only supports one license.",
                solution="Manually specify the license in the dataset_description.json file after conversion.",
                category=Category.SCHEMA_INVALIDATION,
                severity=Severity.WARNING,
            )
            messages.append(message)

    dataset_description = DatasetDescription(**dataset_description_kwargs)
    return dataset_description, messages
