"""Integration tests for the primary `convert_nwb_dataset` function."""

import json
import pathlib

import numpy
import pandas
import pytest

import nwb2bids


def test_minimal_convert_nwb_dataset_from_directory(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path.parent]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    assert len(converter.messages) < 3
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

    assert converter.run_config.notifications_json_file_path.exists()
    with converter.run_config.notifications_json_file_path.open(mode="r") as file_stream:
        notifications_json = json.load(fp=file_stream)
    expected_notification_json = []
    assert notifications_json == expected_notification_json


def test_minimal_convert_nwb_dataset_from_file_path(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
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
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_ecephys_convert_nwb_dataset(ecephys_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb_paths = [ecephys_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-789"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-789": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-789"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-123_ses-789_ecephys.nwb",
                "sub-123_ses-789_channels.tsv",
                "sub-123_ses-789_channels.json",
                "sub-123_ses-789_electrodes.tsv",
                "sub-123_ses-789_electrodes.json",
                "sub-123_ses-789_probes.tsv",
                "sub-123_ses-789_probes.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    probes_tsv_file_path = temporary_bids_directory / "sub-123" / "ses-789" / "ecephys" / "sub-123_ses-789_probes.tsv"
    probes_tsv_dataframe = pandas.read_csv(filepath_or_buffer=probes_tsv_file_path, sep="\t")
    expected_probes_tsv_dataframe = pandas.DataFrame(
        data={
            "probe_id": {0: "Device"},
            "type": {0: numpy.nan},
            "description": {0: "description"},
            "manufacturer": {0: numpy.nan},
        }
    )
    pandas.testing.assert_frame_equal(left=probes_tsv_dataframe, right=expected_probes_tsv_dataframe)


def test_implicit_bids_directory(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    implicit_bids_directory = temporary_bids_directory / "test_convert_nwb_dataset_implicit_bids"
    monkeypatch.chdir(temporary_bids_directory)

    nwb_paths = [minimal_nwbfile_path]
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths)

    expected_structure = {
        implicit_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        implicit_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        implicit_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        implicit_bids_directory
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
        directory=implicit_bids_directory, expected_structure=expected_structure
    )
