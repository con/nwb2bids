"""Unit tests for the NotificationSummary class."""

import json
import pathlib

import pytest

import nwb2bids
from nwb2bids.notifications import Notification, NotificationSummary


@pytest.fixture()
def sample_notifications() -> list[Notification]:
    return [
        Notification.from_definition(identifier="InvalidSpecies"),
        Notification.from_definition(identifier="InvalidParticipantID"),
        Notification.from_definition(identifier="InvalidParticipantSexBIDS"),
    ]


@pytest.fixture()
def notifications_with_paths(tmp_path: pathlib.Path) -> tuple[list[Notification], list[pathlib.Path]]:
    nwb_path = tmp_path / "test.nwb"
    nwb_path.touch()
    nwb_paths = [nwb_path]
    notifications = [
        Notification.from_definition(identifier="InvalidSpecies", source_file_paths=nwb_paths),
        Notification.from_definition(identifier="InvalidSpecies", source_file_paths=nwb_paths),
        Notification.from_definition(identifier="InvalidParticipantID", source_file_paths=nwb_paths),
    ]
    return notifications, nwb_paths


def test_notification_summary_initialization(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications, run_id="test-run-id")
    assert summary.notifications == sample_notifications
    assert summary.run_id == "test-run-id"
    assert isinstance(summary.nwb2bids_version, str)


def test_notification_summary_initialization_no_run_id(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications)
    assert summary.run_id is None


def test_notification_summary_empty() -> None:
    summary = NotificationSummary(notifications=[])
    text = str(summary)
    assert "nwb2bids Inspection Report" in text
    assert "No issues detected." in text


def test_notification_summary_str_contains_header(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications, run_id="test-run-id")
    text = str(summary)
    assert "nwb2bids Inspection Report" in text
    assert "test-run-id" in text
    assert summary.nwb2bids_version in text


def test_notification_summary_str_aggregates_by_default(
    notifications_with_paths: tuple[list[Notification], list[pathlib.Path]],
) -> None:
    notifications, _ = notifications_with_paths
    summary = NotificationSummary(notifications=notifications)
    text = str(summary)
    # "InvalidSpecies" appears twice in notifications but should appear as one block with "2 occurrences"
    assert "2 occurrences" in text
    # InvalidParticipantID appears once
    assert "1 occurrence" in text


def test_notification_summary_str_contains_notification_details(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications)
    text = str(summary)
    assert "Invalid species" in text
    assert "Invalid participant ID" in text
    assert "Invalid participant sex (BIDS)" in text
    # Check severity labels are present
    assert "ERROR" in text


def test_notification_summary_repr(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications, run_id="test-run-id")
    repr_text = repr(summary)
    assert "NotificationSummary" in repr_text
    assert "notifications=3" in repr_text
    assert "test-run-id" in repr_text


def test_notification_summary_to_json_structure(sample_notifications: list[Notification]) -> None:
    summary = NotificationSummary(notifications=sample_notifications, run_id="test-run-id")
    json_str = summary.to_json()
    data = json.loads(json_str)

    assert "nwb2bids_version" in data
    assert data["nwb2bids_version"] == summary.nwb2bids_version
    assert "run_id" in data
    assert data["run_id"] == "test-run-id"
    assert "notifications" in data
    assert len(data["notifications"]) == 3


def test_notification_summary_to_json_full_not_aggregated(
    notifications_with_paths: tuple[list[Notification], list[pathlib.Path]],
) -> None:
    notifications, _ = notifications_with_paths
    summary = NotificationSummary(notifications=notifications)
    json_str = summary.to_json()
    data = json.loads(json_str)
    # to_json always returns all individual notifications (no aggregation)
    assert len(data["notifications"]) == 3


def test_notification_summary_to_file_json_aggregated(
    tmp_path: pathlib.Path,
    notifications_with_paths: tuple[list[Notification], list[pathlib.Path]],
) -> None:
    notifications, _ = notifications_with_paths
    summary = NotificationSummary(notifications=notifications, run_id="test-run")
    out_path = tmp_path / "report.json"
    summary.to_file(path=out_path, aggregate=True)

    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert "nwb2bids_version" in data
    assert data["run_id"] == "test-run"
    # Two unique identifiers: InvalidSpecies (count=2) and InvalidParticipantID (count=1)
    assert len(data["notifications"]) == 2
    species_entry = next(n for n in data["notifications"] if n["identifier"] == "InvalidSpecies")
    assert species_entry["count"] == 2


def test_notification_summary_to_file_json_not_aggregated(
    tmp_path: pathlib.Path,
    notifications_with_paths: tuple[list[Notification], list[pathlib.Path]],
) -> None:
    notifications, _ = notifications_with_paths
    summary = NotificationSummary(notifications=notifications, run_id="test-run")
    out_path = tmp_path / "report.json"
    summary.to_file(path=out_path, aggregate=False)

    assert out_path.exists()
    data = json.loads(out_path.read_text())
    # With aggregate=False, all 3 individual notifications are included
    assert len(data["notifications"]) == 3


def test_notification_summary_to_file_txt(
    tmp_path: pathlib.Path,
    sample_notifications: list[Notification],
) -> None:
    summary = NotificationSummary(notifications=sample_notifications, run_id="test-run")
    out_path = tmp_path / "report.txt"
    summary.to_file(path=out_path)

    assert out_path.exists()
    text = out_path.read_text()
    assert "nwb2bids Inspection Report" in text
    assert "Invalid species" in text


def test_notification_summary_to_file_txt_not_aggregated(
    tmp_path: pathlib.Path,
    notifications_with_paths: tuple[list[Notification], list[pathlib.Path]],
) -> None:
    notifications, _ = notifications_with_paths
    summary = NotificationSummary(notifications=notifications)
    out_path = tmp_path / "report.txt"
    summary.to_file(path=out_path, aggregate=False)

    assert out_path.exists()
    text = out_path.read_text()
    assert "nwb2bids Inspection Report" in text
    # With aggregate=False all 3 entries are separate blocks
    assert text.count("Invalid species") == 2


def test_notification_summary_exported_at_top_level() -> None:
    assert hasattr(nwb2bids, "NotificationSummary")
    assert nwb2bids.NotificationSummary is NotificationSummary


def test_notification_summary_exported_in_notifications_submodule() -> None:
    assert hasattr(nwb2bids.notifications, "NotificationSummary")
    assert nwb2bids.notifications.NotificationSummary is NotificationSummary
