import typing
import warnings

import pydantic

from .._inspection._inspection_result import Category, InspectionResult, Severity
from ..bids_models import DatasetDescription


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
        dataset_description = _get_dataset_description_from_valid_dandiset_metadata(metadata=metadata)
    else:
        dataset_description = None
        messages.append(
            InspectionResult(
                title="NotImplemented: invalid Dandiset metadata",
                reason="This Dandiset has invalid metadata.",
                solution="`nwb2bids` plans to add support for reading from the raw metadata.",
                category=Category.INTERNAL_ERROR,
                severity=Severity.ERROR,
            )
        )

    return dataset_description, messages


def _get_dataset_description_from_valid_dandiset_metadata(metadata: dict) -> DatasetDescription:
    dataset_description_kwargs = dict()

    dataset_description_kwargs["Name"] = metadata.name
    dataset_description_kwargs["BIDSVersion"] = "1.10"

    bids_rrid = "RRID:SCR_016124"
    if any(data_standard.identifier == bids_rrid for data_standard in metadata.assetsSummary.dataStandard):
        message = (
            "Dandiset already contains BIDS content. If only a partial conversion is desired, "
            "please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
        )
        warnings.warn(message=message, category=RuntimeWarning)
        return None

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
    return dataset_description
