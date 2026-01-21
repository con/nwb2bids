import typing

import pydantic

from ..bids_models import DatasetDescription
from ..bids_models._model_globals import _BIDS_RRID
from ..notifications import Category, Notification, Severity


def get_bids_dataset_description(dandiset) -> tuple[DatasetDescription | None, list[Notification]]:
    valid_or_raw: typing.Literal["raw", "valid"] = "valid"
    try:
        metadata = dandiset.get_metadata()
    except pydantic.ValidationError:
        raw_metadata = dandiset.get_raw_metadata()
        valid_or_raw = "raw"

    notifications = []
    if valid_or_raw == "valid":
        dataset_description, internal_messages = _get_dataset_description_from_valid_dandiset_metadata(
            metadata=metadata
        )
        notifications.extend(internal_messages)
    else:
        dataset_description, internal_messages = _get_dataset_description_from_invalid_dandiset_metadata(
            raw_metadata=raw_metadata
        )
        notifications.extend(internal_messages)

        notification = Notification(
            title="INFO: invalid Dandiset metadata",
            reason="This Dandiset has invalid metadata.",
            solution="Required dataset description fields are inferred from the raw metadata instead.",
            category=Category.INTERNAL_ERROR,
            severity=Severity.INFO,
        )
        notifications.append(notification)

    return dataset_description, notifications


def _get_dataset_description_from_valid_dandiset_metadata(
    metadata: typing.Any,
) -> tuple[DatasetDescription | None, list[Notification]]:
    dataset_description_kwargs = dict()

    dataset_description_kwargs["Name"] = metadata.name
    dataset_description_kwargs["BIDSVersion"] = "1.10"
    dataset_description_kwargs["HEDVersion"] = "8.3.0"

    notifications = []
    if any(data_standard.identifier == _BIDS_RRID for data_standard in metadata.assetsSummary.dataStandard):
        notification = Notification.from_definition(notification_id="DandisetAlreadyBIDS")
        notifications.append(notification)
        return None, notifications

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
    return dataset_description, notifications


def _get_dataset_description_from_invalid_dandiset_metadata(
    raw_metadata: dict[str, typing.Any],
) -> tuple[DatasetDescription | None, list[Notification]]:
    dataset_description_kwargs = dict()

    dandiset_identifier = raw_metadata.get("identifier", "??????")
    dataset_description_kwargs["Name"] = raw_metadata.get("name", f"DANDI Archive Dandiset {dandiset_identifier}")
    dataset_description_kwargs["BIDSVersion"] = "1.10"
    dataset_description_kwargs["HEDVersion"] = "8.3.0"

    assets_summary = raw_metadata.get("assetsSummary", dict())
    data_standards = assets_summary.get("dataStandard", [])

    notifications = []
    if any(data_standard.get("identifier", "") == _BIDS_RRID for data_standard in data_standards):
        notification = Notification.from_definition(notification_id="DandisetAlreadyBIDS")
        notifications.append(notification)
        return None, notifications

    dandiset_description = raw_metadata.get("description", None)
    if dandiset_description is not None:
        dataset_description_kwargs["Description"] = dandiset_description

    bids_authors = []
    dandiset_contributors = raw_metadata.get("contributor", [])
    for contributor in dandiset_contributors:
        contributor_name = contributor.get("name", None)
        is_author = "dcite:Author" in contributor.get("roleName", [])
        if contributor_name is not None and is_author:
            bids_authors.append(contributor_name)

    if any(bids_authors):
        dataset_description_kwargs["Authors"] = bids_authors

    license = raw_metadata.get("license", [])
    if len(license) > 0:
        if len(license) == 1:
            dataset_description_kwargs["License"] = license[0].split(":")[-1]
        else:
            notification = Notification(
                title="WARNING: multiple licenses not supported",
                reason="DANDI metadata supports multiple licenses, but BIDS only supports one license.",
                solution="Manually specify the license in the dataset_description.json file after conversion.",
                category=Category.SCHEMA_INVALIDATION,
                severity=Severity.WARNING,
            )
            notifications.append(notification)

    dataset_description = DatasetDescription(**dataset_description_kwargs)
    return dataset_description, notifications
