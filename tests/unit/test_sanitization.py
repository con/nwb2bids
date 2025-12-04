"""
Mostly for demonstration purposes.

The regular expression for labels is trusted to work over all basic cases.
Any edge cases may also be added here to ensure confidence of coverage.
"""

import pathlib

import pytest

import nwb2bids


@pytest.mark.parametrize(
    "participant_id, sanitization_level, expected",
    [
        # Sanitization level NONE should return the original ID
        ("Mouse 12", nwb2bids.sanitization.SanitizationLevel.NONE, "Mouse 12"),
        ("Mouse 12", nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS, "Mouse+12"),
        (
            "Raw/data?sub-01@today",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "Raw+data+sub+01+today",
        ),
    ],
)
def test_sanitize_participant_id(participant_id, sanitization_level, expected, temporary_run_directory: pathlib.Path):
    sanitization_file_path = temporary_run_directory / "test_sanitize_session_id_results.txt"
    sanitization = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id=participant_id,
        original_session_id="12_02_2025",
    )
    assert sanitization.sanitized_participant_id == expected


@pytest.mark.parametrize(
    "session_id, sanitization_level, expected",
    [
        # Sanitization level NONE should return the original ID
        (
            "Session 12 subject 5",
            nwb2bids.sanitization.SanitizationLevel.NONE,
            "Session 12 subject 5",
        ),
        # TODO: think about if subject info in session IDs deserves special cleaning
        (
            "Session 12 subject 5",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "Session+12+subject+5",
        ),
        # TODO: think about if timestamps deserve special cleaning
        (
            "2025-02-03T01:08:12.1236",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "2025+02+03T01+08+12+1236",
        ),
        (
            "12_02_2025",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "12+02+2025",
        ),
    ],
)
def test_sanitize_session_id(session_id, sanitization_level, expected, temporary_run_directory: pathlib.Path):
    sanitization_file_path = temporary_run_directory / "test_sanitize_session_id_results.txt"
    sanitization = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="0",
        original_session_id=session_id,
    )
    assert sanitization.sanitized_session_id == expected
