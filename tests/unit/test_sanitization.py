import nwb2bids


def test_sanitize_participant_id():
    """
    Mostly for demonstration purposes.

    The regular expression is trusted to work over all basic cases.
    Any edge cases may also be added here to ensure confidence of coverage.
    """
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
