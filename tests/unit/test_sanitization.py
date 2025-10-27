"""
Mostly for demonstration purposes.

The regular expression for labels is trusted to work over all basic cases.
Any edge cases may also be added here to ensure confidence of coverage.
"""

import pathlib

import nwb2bids


def test_sanitize_participant_id(temporary_run_directory: pathlib.Path) -> None:
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS
    sanitization_file_path = temporary_run_directory / "test_sanitize_participant_id_results.txt"

    sanitization_case_1 = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="Mouse 12",
        original_session_id="0",
    )
    assert sanitization_case_1.sanitized_participant_id == "Mouse+12"

    sanitization_case_2 = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="Raw/data?sub-01@today",
        original_session_id="0",
    )
    assert sanitization_case_2.sanitized_participant_id == "Raw+data+sub+01+today"


def test_sanitize_session_id(temporary_run_directory: pathlib.Path) -> None:
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS
    sanitization_file_path = temporary_run_directory / "test_sanitize_session_id_results.txt"

    # TODO: think about if subject info in session IDs deserves special cleaning
    sanitization_case_1 = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="0",
        original_session_id="Session 12 subject 5",
    )
    assert sanitization_case_1.sanitized_session_id == "Session+12+subject+5"

    # TODO: think about if timestamps deserve special cleaning
    sanitization_case_2 = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="0",
        original_session_id="2025-02-03T01:08:12.1236",
    )
    assert sanitization_case_2.sanitized_session_id == "2025+02+03T01+08+12+1236"

    sanitization_case_3 = nwb2bids.sanitization.Sanitization(
        sanitization_level=sanitization_level,
        sanitization_file_path=sanitization_file_path,
        original_participant_id="0",
        original_session_id="12_02_2025",
    )
    assert sanitization_case_3.sanitized_session_id == "12+02+2025"
