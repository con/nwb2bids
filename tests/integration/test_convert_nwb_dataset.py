"""Integration tests for the primary `convert_nwb_dataset` function."""

import json
import pathlib

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
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    assert not any(converter.messages)

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-001"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-001": {
            "directories": {"ses-A"},
            "files": {"sub-001_sessions.json", "sub-001_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-001"
        / "ses-A": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-001"
        / "ses-A"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-001_ses-A_ecephys.nwb",
                "sub-001_ses-A_channels.tsv",
                "sub-001_ses-A_channels.json",
                "sub-001_ses-A_electrodes.tsv",
                "sub-001_ses-A_electrodes.json",
                "sub-001_ses-A_probes.tsv",
                "sub-001_ses-A_probes.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    probes_tsv_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_probes.tsv"
    probes_tsv_lines = probes_tsv_file_path.read_text().splitlines()
    expected_probe_tsv_lines = [
        "probe_name\ttype\tdescription\tmanufacturer",
        "ExampleProbe\tN/A\tThis is an example probe used for demonstration purposes.\t`nwb2bids.testing` module",
    ]
    assert probes_tsv_lines == expected_probe_tsv_lines

    electrodes_tsv_file_path = (
        temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.tsv"
    )
    electrodes_tsv_lines = electrodes_tsv_file_path.read_text().splitlines()
    expected_electrodes_tsv_lines = [
        "name\tprobe_name\themisphere\tx\ty\tz\timpedance\tshank_id\tlocation",
        "e000\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e001\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e002\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e003\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e004\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e005\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e006\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
        "e007\tExampleProbe\tN/A\tN/A\tN/A\tN/A\t150.0\tExampleShank\thippocampus",
    ]
    assert electrodes_tsv_lines == expected_electrodes_tsv_lines

    channels_tsv_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.tsv"
    channels_tsv_lines = channels_tsv_file_path.read_text().splitlines()
    expected_channels_tsv_lines = [
        "channel_name\treference\ttype\tunit\tsampling_frequency\tchannel_label\t"
        "stream_id\tdescription\thardware_filters\tsoftware_filters\tstatus\t"
        "status_description\tgain\ttime_offset\ttime_reference_channels\tground",
        "ch0\t0\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch1\t1\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch2\t2\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch3\t3\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch4\t4\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch5\t5\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch6\t6\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
        "ch7\t7\tN/A\tV\t\t\t\t\tHighpassFilter\tN/A\t\t\t\t\t\t",
    ]
    assert channels_tsv_lines == expected_channels_tsv_lines


# TODO: in follow-up, add test that checks if manufacturer column is dropped when empty


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
