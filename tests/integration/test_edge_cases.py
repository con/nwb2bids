"""
Integration tests for edge cases of the primary `convert_nwb_dataset` function.

Namely, the cases of:
  - A dataset with additional metadata and the case of a dataset.
  - A dataset without a session ID.
"""

import pathlib

import pydantic

import nwb2bids


def test_convert_nwb_dataset_with_additional_metadata(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=minimal_nwbfile_path.parent,
        bids_directory=temporary_bids_directory,
        additional_metadata_file_path=additional_metadata_file_path,
    )

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
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
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_convert_nwb_dataset_no_session_id(
    nwbfile_path_with_missing_session_id: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    try:
        nwb2bids.convert_nwb_dataset(
            nwb_directory=nwbfile_path_with_missing_session_id.parent, bids_directory=temporary_bids_directory
        )
    except Exception as exception:
        assert isinstance(exception, pydantic.ValidationError)
        assert "session_id\n  Input should be a valid string" in str(exception)
