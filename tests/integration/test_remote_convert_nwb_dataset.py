import pathlib

import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_dataset_converter(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003", limit=3)
    dataset_converter.extract_metadata()
    dataset_converter.convert_to_bids_dataset(bids_directory=temporary_bids_directory)

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
