import pathlib

import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_convert_nwb_dataset(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(
        dandiset_id="000003", limit=2, run_config=run_config
    )
    dataset_converter.extract_metadata()
    dataset_converter.convert_to_bids_dataset()

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-YutaMouse20"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-YutaMouse20": {
            "directories": {"ses-YutaMouse20-140321", "ses-YutaMouse20-140327"},
            "files": {"sub-YutaMouse20_sessions.json", "sub-YutaMouse20_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-YutaMouse20"
        / "ses-YutaMouse20-140321": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-YutaMouse20"
        / "ses-YutaMouse20-140327": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-YutaMouse20"
        / "ses-YutaMouse20-140321"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-YutaMouse20_ses-YutaMouse20-140321_channels.json",
                "sub-YutaMouse20_ses-YutaMouse20-140321_channels.tsv",
                "sub-YutaMouse20_ses-YutaMouse20-140321_ecephys.nwb",
                "sub-YutaMouse20_ses-YutaMouse20-140321_electrodes.json",
                "sub-YutaMouse20_ses-YutaMouse20-140321_electrodes.tsv",
                "sub-YutaMouse20_ses-YutaMouse20-140321_probes.json",
                "sub-YutaMouse20_ses-YutaMouse20-140321_probes.tsv",
            },
        },
        temporary_bids_directory
        / "sub-YutaMouse20"
        / "ses-YutaMouse20-140327"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-YutaMouse20_ses-YutaMouse20-140327_channels.json",
                "sub-YutaMouse20_ses-YutaMouse20-140327_channels.tsv",
                "sub-YutaMouse20_ses-YutaMouse20-140327_ecephys.nwb",
                "sub-YutaMouse20_ses-YutaMouse20-140327_electrodes.json",
                "sub-YutaMouse20_ses-YutaMouse20-140327_electrodes.tsv",
                "sub-YutaMouse20_ses-YutaMouse20-140327_probes.json",
                "sub-YutaMouse20_ses-YutaMouse20-140327_probes.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
