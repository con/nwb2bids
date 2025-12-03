"""
Mostly for demonstration purposes.

The regular expression for labels is trusted to work over all basic cases.
Any edge cases may also be added here to ensure confidence of coverage.
"""

import pytest

import nwb2bids


@pytest.mark.parametrize(
    "participant_id, expected",
    [
        ("Mouse 12", "Mouse+12"),
        ("Raw/data?sub-01@today", "Raw+data+sub+01+today"),
    ],
)
def test_sanitize_participant_id(participant_id, expected):
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS

    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id=participant_id, sanitization_level=sanitization_level
        )
        == expected
    )


@pytest.mark.parametrize(
    "session_id, expected",
    [
        # TODO: think about if subject info in session IDs deserves special cleaning
        ("Session 12 subject 5", "Session+12+subject+5"),
        # TODO: think about if timestamps deserve special cleaning
        ("2025-02-03T01:08:12.1236", "2025+02+03T01+08+12+1236"),
        ("12_02_2025", "12+02+2025"),
    ],
)
def test_sanitize_session_id(session_id, expected):
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS

    assert (
        nwb2bids.sanitization.sanitize_session_id(session_id=session_id, sanitization_level=sanitization_level)
        == expected
    )
