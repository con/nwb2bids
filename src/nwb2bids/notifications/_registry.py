import pathlib

import pydantic
import typing_extensions

from ._notification import Category, DataStandard, Notification, Severity

# Proposal 0: Current approach - same class, different instances
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

registry: dict[str, Notification] = {notification.title: notification for notification in [a]}
# Note how the title currently has spaces; shorter codes/aliases could be added for easier lookup in the dictionary



# Proposal 1: Child classes with mostly hard-coded fields followed by mutation
class MissingParticipantID1(Notification):
    title = "Missing participant ID"
    reason = "A unique ID is required for all individual participants."
    solution = "Specify the `subject_id` field of the Subject object attached to the NWB file."
    field = "nwbfile.subject.subject_id"
    data_standards = [DataStandard.BIDS, DataStandard.DANDI]
    category = Category.SCHEMA_INVALIDATION
    severity = Severity.CRITICAL


b = MissingParticipantID1
b.source_file_paths = ["Proposal1.nwb"]

registry: dict[str, Notification] = {notification.__name__: notification for notification in [b]}


# Proposal 2: Child classes with mostly internal hard-coded values followed by class method instantiation for dynamic parts
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

c = MissingParticipantID2.from_paths(file_paths=["Proposal2.nwb"])

registry: dict[str, Notification] = {notification.__name__: notification for notification in [c]}



# Proposal 3: Factory class
_internal_hardcoded_values: dict[str, dict[str, str]] = {
    "MissingParticipantID": {
        "title": "Missing participant ID",
        "reason": "A unique ID is required for all individual participants.",
        ...etc
    },
    # ... more types
}
# NOTE: this dictionary could/should be stored outside the Python in some JSON or YAML file

class Notification:
    @classmethod
    def from_paths(cls, notification_type: str, file_paths: list):
        return cls(**NOTIFICATIONS[notification_type], notification_type=notification_type, source_file_paths=file_paths)

d = Notification.from_paths(notification_type=MissingParticipantID, file_paths=["Proposal3.nwb"])

registry: dict[str, Notification] = {notification.notification_type: notification for notification in [d]}

