"""
Mostly for demonstration purposes.

The regular expression for labels is trusted to work over all basic cases.
Any edge cases may also be added here to ensure confidence of coverage.
"""

import pytest

import nwb2bids


@pytest.mark.parametrize(
    "participant_id, sanitization_level, expected",
    [
        ("Mouse 12", nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS, "Mouse+12"),
        (
            "Raw/data?sub-01@today",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "Raw+data+sub+01+today",
        ),
    ],
)
def test_sanitize_participant_id(participant_id, sanitization_level, expected):
    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id=participant_id, sanitization_level=sanitization_level
        )
        == expected
    )


@pytest.mark.parametrize(
    "session_id, sanitization_level, expected",
    [
        # TODO: think about if subject info in session IDs deserves special cleaning
        ("Session 12 subject 5", nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS, "Session+12+subject+5"),
        # TODO: think about if timestamps deserve special cleaning
        (
            "2025-02-03T01:08:12.1236",
            nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
            "2025+02+03T01+08+12+1236",
        ),
        ("12_02_2025", nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS, "12+02+2025"),
    ],
)
def test_sanitize_session_id(session_id, sanitization_level, expected):
    assert (
        nwb2bids.sanitization.sanitize_session_id(session_id=session_id, sanitization_level=sanitization_level)
        == expected
    )
