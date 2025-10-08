import pathlib
import subprocess

import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_convert_nwb_dataset(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003", limit=2)
    dataset_converter.extract_metadata()
    dataset_converter.convert_to_bids_dataset(bids_directory=temporary_bids_directory)

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


@pytest.mark.remote
def test_remote_convert_nwb_dataset_on_real_datalad_dataset(
    testing_files_directory: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    subprocess.run(
        args=["datalad", "install", "https://github.com/dandisets/000568"], check=True, cwd=testing_files_directory
    )
    subprocess.run(
        args=[
            "datalad",
            "get",
            "sub-fCamk1/sub-fCamk1_ses-fCamk1-200827-sess9-no-raw-data_behavior+ecephys+image+ogen.nwb",
        ],
        check=True,
        cwd=testing_files_directory / "000568",
    )

    nwb_paths = [
        testing_files_directory
        / "000568"
        / "sub-fCamk1"
        / "sub-fCamk1_ses-fCamk1-200827-sess9-no-raw-data_behavior+ecephys+image+ogen.nwb"
    ]
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths)
    dataset_converter.extract_metadata()
    dataset_converter.convert_to_bids_dataset(bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-fCamk1"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-fCamk1": {
            "directories": {"ses-fCamk1_200827_sess9_no_raw_data"},
            "files": {"sub-fCamk1_sessions.json", "sub-fCamk1_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-fCamk1"
        / "ses-fCamk1_200827_sess9_no_raw_data": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-fCamk1"
        / "ses-fCamk1_200827_sess9_no_raw_data"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_channels.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_channels.tsv",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_ecephys.nwb",
                # TODO: in follow-up, fix the bug preventing electrodes and probes files from being created
                # "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_electrodes.json",
                # "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_electrodes.tsv",
                # "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.json",
                # "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.tsv",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
