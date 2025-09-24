import typing

import pydantic

from .._inspection._inspection_result import Category, InspectionResult, Severity
from ..bids_models import DatasetDescription
from ..bids_models._model_globals import _BIDS_RRID


def get_bids_dataset_description(dandiset) -> tuple[DatasetDescription, list[InspectionResult]]:
    valid_or_raw: typing.Literal["raw", "valid"] = "valid"
    try:
        metadata = dandiset.get_metadata()
    except pydantic.ValidationError:
        # TODO
        # raw_dandiset_metadata = dandiset.get_raw_metadata()
        valid_or_raw = "raw"

    messages = []
    if valid_or_raw == "valid":
        dataset_description, internal_messages = _get_dataset_description_from_valid_dandiset_metadata(
            metadata=metadata
        )
        messages.extend(internal_messages)
    else:
        dataset_description = None
        message = InspectionResult(
            title="NotImplemented: invalid Dandiset metadata",
            reason="This Dandiset has invalid metadata.",
            solution="`nwb2bids` plans to add support for reading from the raw metadata.",
            category=Category.INTERNAL_ERROR,
            severity=Severity.ERROR,
        )
        messages.append(message)

    return dataset_description, messages


def _get_dataset_description_from_valid_dandiset_metadata(
    metadata: dict,
) -> tuple[DatasetDescription, list[InspectionResult]]:
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
