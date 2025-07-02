"""
Integration tests for edge cases of the primary `convert_nwb_dataset` function.

Namely, the cases of:
  - A dataset with additional metadata and the case of a dataset.
  - A dataset without a session ID.
"""

import pathlib

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
            "directories": {"sub-12X34"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
        temporary_bids_directory
        / "sub-12X34": {
            "directories": {"ses-20240309"},
            "files": {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-12X34"
        / "ses-20240309": {
            "directories": {"ephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-12X34"
        / "ses-20240309"
        / "ephys": {
            "directories": set(),
            "files": {
                "sub-12X34_ses-20240309_channels.tsv",
                "sub-12X34_ses-20240309_electrodes.tsv",
                "sub-12X34_ses-20240309_ephys.nwb",
                "sub-12X34_ses-20240309_probes.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_convert_nwb_dataset_no_session_id(
    nwbfile_path_with_missing_session_id: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=nwbfile_path_with_missing_session_id.parent, bids_directory=temporary_bids_directory
    )

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-12X34"}, "files": {"participants.json", "participants.tsv"}},
        temporary_bids_directory
        / "sub-12X34": {
            "directories": {"ephys"},
            "files": {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-12X34"
        / "ephys": {
            "directories": set(),
            "files": {
                "sub-12X34_channels.tsv",
                "sub-12X34_ephys.nwb",
                "sub-12X34_electrodes.tsv",
                "sub-12X34_probes.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
