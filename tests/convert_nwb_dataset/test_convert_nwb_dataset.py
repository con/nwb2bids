"""Integration tests for the primary `convert_nwb_dataset` function."""

import pathlib

import nwb2bids


def test_convert_nwb_dataset(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    nwb2bids.convert_nwb_dataset(nwb_directory=minimal_nwbfile_path.parent, bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-12X34"}, "files": {"participants.json", "participants.tsv"}},
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
