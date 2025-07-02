"""Integration tests for the primary `convert_nwb_dataset` function with events data."""

import pathlib

import nwb2bids


def test_trials_events(trials_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=trials_events_nwbfile_path.parent, bids_directory=temporary_bids_directory
    )

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": {"participants.json", "participants.tsv"}},
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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_epochs_events(epochs_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=epochs_events_nwbfile_path.parent, bids_directory=temporary_bids_directory
    )

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": {"participants.json", "participants.tsv"}},
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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_multiple_events(multiple_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=multiple_events_nwbfile_path.parent, bids_directory=temporary_bids_directory
    )

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv"},
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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
