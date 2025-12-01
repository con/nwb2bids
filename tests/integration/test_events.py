"""Integration tests for the primary `convert_nwb_dataset` function with events data."""

import json
import pathlib

import nwb2bids


def test_trials_events(trials_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [trials_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    json_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.json"
    expected_json_content = {
        "nwb_table": {
            "nwb_table": {
                "Description": "The name of the NWB table from " "which this event was extracted.",
                "HED": {"trials": "Experimental-trial"},
                "Levels": {"trials": "The 'trials' table in the " "NWB file."},
            }
        },
        "trials": {"Description": "A mock trials table."},
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content


def test_epochs_events(epochs_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [epochs_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    json_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.json"
    expected_json_content = {
        "epochs": {"Description": "A mock epochs table."},
        "nwb_table": {
            "nwb_table": {
                "Description": "The name of the NWB table from " "which this event was extracted.",
                "HED": {"epochs": "Time-block"},
                "Levels": {"epochs": "The 'epochs' table in the " "NWB file."},
            }
        },
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content


def test_multiple_events(multiple_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [multiple_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

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
                "sub-123_ses-456_events.tsv",
                "sub-123_ses-456_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    json_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.json"
    expected_json_content = {
        "epochs": {"Description": "A mock epochs table."},
        "mock_time_intervals": {"Description": "A mock time intervals table."},
        "nwb_table": {
            "nwb_table": {
                "Description": "The name of the NWB table from " "which this event was extracted.",
                "HED": {"epochs": "Time-block", "mock_time_intervals": "Time-interval", "trials": "Experimental-trial"},
                "Levels": {
                    "epochs": "The 'epochs' table in the " "NWB file.",
                    "mock_time_intervals": "The " "'mock_time_intervals' " "table in the " "NWB file.",
                    "trials": "The 'trials' table in the " "NWB file.",
                },
            }
        },
        "trials": {"Description": "A mock trials table."},
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content
