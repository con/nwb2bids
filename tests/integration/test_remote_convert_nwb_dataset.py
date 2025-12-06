import pathlib

import datalad.api
import pytest

import nwb2bids
from tests.conftest import pytest_mark_xfail_windows_github_ci


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


@pytest.mark.remote
@pytest_mark_xfail_windows_github_ci
def test_remote_convert_nwb_dataset_on_gotten_datalad_file(
    testing_files_directory: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    dataset_dir = testing_files_directory / "000568"
    dataset_dir.mkdir(exist_ok=True)

    dataset = datalad.api.clone(source="https://github.com/dandisets/000568", path=dataset_dir)

    filename = "sub-fCamk1_ses-fCamk1-200827-sess9-no-raw-data_behavior+ecephys+image+ogen.nwb"
    test_file_path = dataset_dir / "sub-fCamk1" / filename
    dataset.get(path=test_file_path)

    nwb_paths = [test_file_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    notifications = converter.messages

    assert len(notifications) < 2, "Expected fewer than 2 notifications!"
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
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.tsv",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


@pytest.mark.remote
@pytest_mark_xfail_windows_github_ci
def test_remote_convert_nwb_dataset_on_partial_datalad_dataset(
    testing_files_directory: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    dataset_dir = testing_files_directory / "000568"
    dataset_dir.mkdir(exist_ok=True)

    dataset = datalad.api.clone(source="https://github.com/dandisets/000568", path=dataset_dir)

    filename = "sub-fCamk1_ses-fCamk1-200827-sess9-no-raw-data_behavior+ecephys+image+ogen.nwb"
    test_file_path = dataset_dir / "sub-fCamk1" / filename
    dataset.get(path=test_file_path)

    nwb_paths = [dataset_dir]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    notifications = converter.messages

    assert len(notifications) < 2, "Expected fewer than 2 notifications!"
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
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_probes.tsv",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.json",
                "sub-fCamk1_ses-fCamk1_200827_sess9_no_raw_data_events.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
