"""
Mostly for demonstration purposes.

The regular expression for labels is trusted to work over all basic cases.
Any edge cases may also be added here to ensure confidence of coverage.
"""

import nwb2bids


def test_sanitize_participant_id():
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS

    assert (
        nwb2bids.sanitization.sanitize_participant_id(participant_id="Mouse 12", sanitization_level=sanitization_level)
        == "Mouse+12"
    )
    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id="Raw/data?sub-01@today", sanitization_level=sanitization_level
        )
        == "Raw+data+sub+01+today"
    )


def test_sanitize_session_id():
    sanitization_level = nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS

    # TODO: think about if subject info in session IDs deserves special cleaning
    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id="Session 12 subject 5", sanitization_level=sanitization_level
        )
        == "Session+12+subject+5"
    )

    # TODO: think about if timestamps deserve special cleaning
    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id="2025-02-03T01:08:12.1236", sanitization_level=sanitization_level
        )
        == "2025+02+03T01+08+12+1236"
    )

    assert (
        nwb2bids.sanitization.sanitize_participant_id(
            participant_id="12_02_2025", sanitization_level=sanitization_level
        )
        == "12+02+2025"
    )
