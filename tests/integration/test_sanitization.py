"""Sanitization tests for the API."""

import pathlib

import nwb2bids


def test_convert_nwb_dataset_level_1_sanitization(
    problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [problematic_nwbfile_path_2]
    notifications = nwb2bids.convert_nwb_dataset(
        nwb_paths=nwb_paths,
        bids_directory=temporary_bids_directory,
        sanitization_level=nwb2bids.sanitization.SanitizationLevel.CRITICAL_BIDS_LABELS,
    )

    assert len(notifications) == 0
    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-123_ses-456_ecephys.nwb",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
