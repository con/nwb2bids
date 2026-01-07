import pathlib

import pydantic
import typing_extensions

from ._notification import Category, DataStandard, Notification, Severity

a = Notification(
    title="Missing participant ID",
    reason="A unique ID is required for all individual participants.",
    solution="Specify the `subject_id` field of the Subject object attached to the NWB file.",
    field="nwbfile.subject.subject_id",
    source_file_paths="Test1",
    data_standards=[DataStandard.BIDS, DataStandard.DANDI],
    category=Category.SCHEMA_INVALIDATION,
    severity=Severity.CRITICAL,
)


class MissingParticipantID(Notification):
    title = "Missing participant ID"
    reason = "A unique ID is required for all individual participants."
    solution = "Specify the `subject_id` field of the Subject object attached to the NWB file."
    field = "nwbfile.subject.subject_id"
    data_standards = [DataStandard.BIDS, DataStandard.DANDI]
    category = Category.SCHEMA_INVALIDATION
    severity = Severity.CRITICAL


b = MissingParticipantID
b.source_file_paths = "Test2"


class MissingParticipantID2(Notification):
    @classmethod
    def from_paths(cls, file_paths: list[pathlib.Path] | list[pydantic.HttpUrl]) -> typing_extensions.Self:
        instance = cls(
            title="Missing participant ID",
            reason="A unique ID is required for all individual participants.",
            solution="Specify the `subject_id` field of the Subject object attached to the NWB file.",
            field="nwbfile.subject.subject_id",
            source_file_paths=file_paths,
            data_standards=[DataStandard.BIDS, DataStandard.DANDI],
            category=Category.SCHEMA_INVALIDATION,
            severity=Severity.CRITICAL,
        )
        return instance


c = MissingParticipantID.from_paths(file_paths=["Test3"])
