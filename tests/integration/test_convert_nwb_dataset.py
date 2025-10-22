"""Integration tests for the primary `convert_nwb_dataset` function."""

import pathlib

import pytest

import nwb2bids


def test_minimal_convert_nwb_dataset_from_directory(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path.parent]
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

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


def test_minimal_convert_nwb_dataset_from_file_path(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

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
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

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


def test_optional_bids_directory(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path, monkeypatch
):
    new_bids_directory = temporary_bids_directory / "bids"
    monkeypatch.chdir(temporary_bids_directory)

    nwb_paths = [minimal_nwbfile_path]
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths)

    expected_structure = {
        new_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        new_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        new_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        new_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-123_ses-456_ecephys.nwb",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=new_bids_directory, expected_structure=expected_structure)


def test_convert_empty_nwb_paths(tmp_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    """
    Test the case that no NWB files are found in the provided paths.
    """

    # Set up empty directory structure
    dir_1 = tmp_path / "dir_1"
    dir_1_1 = dir_1 / "dir_1_1"
    dir_1_1_1 = dir_1_1 / "dir_1_1_1"
    dir_2 = tmp_path / "dir_2"
    dir_1_1_1.mkdir(parents=True)
    dir_2.mkdir()
    text_file = dir_2 / "not_an_nwb_file.txt"
    text_file.write_text("This is not an NWB file.")

    nwb_paths = [dir_1, dir_2]

    with pytest.raises(ValueError, match="No NWB files found in the provided paths."):
        nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)
