"""Integration tests for the primary `convert_nwb_dataset` function with events data."""

import json
import pathlib

import pandas
import pytest

import nwb2bids


def test_trials_events(trials_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [trials_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, use_session_labels=True)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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

    tsv_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.tsv"
    actual_dataframe = pandas.read_csv(filepath_or_buffer=tsv_file_path, sep="\t")
    expected_dataframe = pandas.DataFrame(
        {
            "onset": {0: 0.0, 1: 2.0, 2: 5.0, 3: 5.5},
            "duration": {0: 1.0, 1: 1.0, 2: 0.5, 3: 0.5},
            "nwb_table": {0: "trials", 1: "trials", 2: "trials", 3: "trials"},
            "trial_condition": {0: "A", 1: "B", 2: "C", 3: "D"},
        }
    )
    pandas.testing.assert_frame_equal(left=actual_dataframe, right=expected_dataframe)

    json_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.json"
    expected_json_content = {
        "onset": {"Description": "Onset of the event, measured from the beginning of the acquisition.", "Units": "s"},
        "duration": {"Description": "Duration of the event (measured from onset).", "Units": "s"},
        "trial_condition": {"Description": "Extra information per trial."},
        "nwb_table": {
            "Description": "The name of the NWB table from which this event was extracted.",
            "HED": {"trials": "Experimental-trial"},
            "Levels": {"trials": "The 'trials' table in the NWB file."},
        },
        "trials": {"Description": "A mock trials table."},
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content


def test_epochs_events(epochs_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [epochs_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, use_session_labels=True)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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
        "onset": {"Description": "Onset of the event, measured from the beginning of the acquisition.", "Units": "s"},
        "duration": {"Description": "Duration of the event (measured from onset).", "Units": "s"},
        "epoch_condition": {"Description": "Extra information per epoch."},
        "nwb_table": {
            "Description": "The name of the NWB table from which this event was extracted.",
            "HED": {"epochs": "Time-block"},
            "Levels": {"epochs": "The 'epochs' table in the NWB file."},
        },
        "epochs": {"Description": "A mock epochs table."},
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content


def test_multiple_events(multiple_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [multiple_events_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, use_session_labels=True)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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
        "onset": {"Description": "Onset of the event, measured from the beginning of the acquisition.", "Units": "s"},
        "duration": {"Description": "Duration of the event (measured from onset).", "Units": "s"},
        "trial_condition": {"Description": "Extra information per trial."},
        "epoch_condition": {"Description": "Extra information per epoch."},
        "tag": {"Description": "A tag assigned to each interval."},
        "nwb_table": {
            "Description": "The name of the NWB table from which this event was extracted.",
            "HED": {"epochs": "Time-block", "mock_time_intervals": "Time-interval", "trials": "Experimental-trial"},
            "Levels": {
                "epochs": "The 'epochs' table in the NWB file.",
                "mock_time_intervals": "The 'mock_time_intervals' table in the NWB file.",
                "trials": "The 'trials' table in the NWB file.",
            },
        },
        "trials": {"Description": "A mock trials table."},
        "epochs": {"Description": "A mock epochs table."},
        "mock_time_intervals": {"Description": "A mock time intervals table."},
    }
    with json_file_path.open(mode="r") as file_stream:
        actual_json_content = json.load(fp=file_stream)
    assert actual_json_content == expected_json_content


@pytest.mark.ai_generated
def test_trials_events_with_numpy_array_column(
    trials_with_numpy_column_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Regression test: numpy array-valued columns must be serialized to JSON strings in the TSV output.

    Reproduces https://github.com/con/nwb2bids/issues/338 – when a column stores a fixed-size array
    per trial, numpy's default ``__str__`` inserts line-breaks into wide arrays, which broke TSV rows.
    """
    nwb_paths = [trials_with_numpy_column_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, use_session_labels=True)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    tsv_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.tsv"
    with tsv_file_path.open(mode="r") as file_stream:
        content = file_stream.read()

    # Each data row must occupy exactly one line (no embedded newlines from numpy string formatting)
    lines = content.splitlines()
    assert len(lines) == 3, f"Expected 3 lines (header + 2 data rows), got {len(lines)}: {lines}"

    # The pulse_times values must be valid JSON arrays (no embedded newlines)
    actual_dataframe = pandas.read_csv(filepath_or_buffer=tsv_file_path, sep="\t")
    assert "pulse_times" in actual_dataframe.columns
    for cell_value in actual_dataframe["pulse_times"]:
        parsed = json.loads(cell_value)
        assert isinstance(parsed, list)
