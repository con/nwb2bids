"""Unit tests for the `SessionConverter` class and its methods."""

import json
import pathlib

import pandas

import nwb2bids


def test_session_converter_initialization(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)

    assert isinstance(session_converters, list)
    assert len(session_converters) == 1
    assert isinstance(session_converters[0], nwb2bids.SessionConverter)


def test_session_converter_metadata_extraction(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    session_converters[0].extract_session_metadata()

    expected_session_metadata = nwb2bids.bids_models.BidsSessionMetadata(
        session_id="456",
        participant=nwb2bids.bids_models.Participant(participant_id="123", species="Mus musculus", sex="male"),
        extra={
            "session": {"session_id": "456", "number_of_trials": None, "comments": "session_description"},
            "participant": {"participant_id": "123", "species": "Mus musculus", "strain": None, "sex": "male"},
            "probes": [],
        },
    )
    assert session_converters[0].session_metadata == expected_session_metadata


def test_session_converter_write_ecephys_metadata(
    ecephys_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=ecephys_nwbfile_path.parent)
    session_converter = session_converters[0]
    session_converter.extract_session_metadata()
    session_converter.write_ecephys_files(bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": set()},
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": set(),
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
                "sub-123_ses-456_probes.tsv",
                "sub-123_ses-456_probes.json",
                "sub-123_ses-456_channels.tsv",
                "sub-123_ses-456_channels.json",
                "sub-123_ses-456_electrodes.tsv",
                "sub-123_ses-456_electrodes.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    # TODO: assert contents of TSV and JSON files


def test_session_converter_write_events_metadata(
    trials_events_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=trials_events_nwbfile_path.parent)
    session_converter = session_converters[0]
    session_converter.extract_session_metadata()
    session_converter.write_events_files(bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": set()},
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": set(),
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
            "files": {"sub-123_ses-456_events.tsv", "sub-123_ses-456_events.json"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    sessions_tsv_file_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.tsv"
    sessions_data_frame = pandas.read_csv(filepath_or_buffer=sessions_tsv_file_path, sep="\t")

    expected_data_frame = pandas.DataFrame(
        {
            "onset": [0.0, 2.0, 5.0, 5.5],
            "duration": [1.0, 1.0, 0.5, 0.5],
            "nwb_table": ["trials", "trials", "trials", "trials"],
            "trial_condition": ["A", "B", "C", "D"],
        },
    )
    pandas.testing.assert_frame_equal(left=sessions_data_frame, right=expected_data_frame)

    sessions_json_file_path = (
        temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_events.json"
    )
    with sessions_json_file_path.open(mode="r") as file_stream:
        sessions_json = json.load(fp=file_stream)
    expected_sessions_json = {
        "trials": {"Description": "A mock trials table."},
        "nwb_table": {
            "nwb_table": {
                "Description": "The name of the NWB table from which this event was extracted.",
                "Levels": {"trials": "The 'trials' table in the NWB file."},
                "HED": {"trials": "Experimental-trial"},
            }
        },
    }
    assert sessions_json == expected_sessions_json
