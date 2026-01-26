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
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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

    assert dataset_converter.run_config.notifications_json_file_path.exists()
    with dataset_converter.run_config.notifications_json_file_path.open(mode="r") as file_stream:
        notifications_json = json.load(fp=file_stream)
    expected_notification_json = []
    assert notifications_json == expected_notification_json


def test_minimal_convert_nwb_dataset_from_file_path(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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


def test_ecephys_tutorial_convert_nwb_dataset(
    ecephys_tutorial_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [ecephys_tutorial_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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
        "probe_name\ttype\tmanufacturer\tdescription",
        (
            "ExampleProbe\tn/a\t`nwb2bids.testing` module\tThis is an example ecephys probe "
            "used for demonstration purposes."
        ),
    ]
    assert probes_tsv_lines == expected_probe_tsv_lines

    electrodes_tsv_file_path = (
        temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.tsv"
    )
    electrodes_tsv_lines = electrodes_tsv_file_path.read_text().splitlines()
    expected_electrodes_tsv_lines = [
        "name\tprobe_name\tx\ty\tz\themisphere\timpedance\tshank_id\tlocation",
        "e000\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e001\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e002\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e003\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e004\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e005\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e006\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
        "e007\tExampleProbe\tn/a\tn/a\tn/a\tn/a\t150.0\tExampleShank\thippocampus",
    ]
    assert electrodes_tsv_lines == expected_electrodes_tsv_lines

    channels_tsv_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.tsv"
    channels_tsv_lines = channels_tsv_file_path.read_text().splitlines()
    expected_channels_tsv_lines = [
        "name\telectrode_name\ttype\tunits\tsampling_frequency\tstream_id\tgain",
        "ch000\te000\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch001\te001\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch002\te002\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch003\te003\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch004\te004\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch005\te005\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch006\te006\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
        "ch007\te007\tn/a\tV\t30000.0\tExampleElectricalSeries\t3.02734375e-06",
    ]
    assert channels_tsv_lines == expected_channels_tsv_lines


def test_ecephys_minimal_convert_nwb_dataset(
    ecephys_minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [ecephys_minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

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
        "probe_name\ttype\tdescription",
        "ExampleProbe\tn/a\tThis is an example probe used for demonstration purposes.",
    ]
    assert probes_tsv_lines == expected_probe_tsv_lines

    electrodes_tsv_file_path = (
        temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.tsv"
    )
    electrodes_tsv_lines = electrodes_tsv_file_path.read_text().splitlines()
    expected_electrodes_tsv_lines = [
        "name\tprobe_name\tx\ty\tz\themisphere\timpedance\tshank_id\tlocation",
        "e000\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e001\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e002\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e003\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e004\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e005\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e006\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
        "e007\tExampleProbe\tn/a\tn/a\tn/a\tn/a\tn/a\tExampleShank\tn/a",
    ]
    assert electrodes_tsv_lines == expected_electrodes_tsv_lines

    channels_tsv_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.tsv"
    channels_tsv_lines = channels_tsv_file_path.read_text().splitlines()
    expected_channels_tsv_lines = [
        "name\telectrode_name\ttype\tunits",
        "ch000\te000\tn/a\tV",
        "ch001\te001\tn/a\tV",
        "ch002\te002\tn/a\tV",
        "ch003\te003\tn/a\tV",
        "ch004\te004\tn/a\tV",
        "ch005\te005\tn/a\tV",
        "ch006\te006\tn/a\tV",
        "ch007\te007\tn/a\tV",
    ]
    assert channels_tsv_lines == expected_channels_tsv_lines


# TODO: in follow-up, add test that checks if manufacturer column is dropped when empty


def test_implicit_bids_directory(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    implicit_bids_directory = temporary_bids_directory / "test_convert_nwb_dataset_implicit_bids"
    monkeypatch.chdir(temporary_bids_directory)

    nwb_paths = [minimal_nwbfile_path]
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths)
    assert not any(dataset_converter.notifications)

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


def test_implicit_bids_directory_with_relative_nwb_paths(
    minimal_nwbfile_path: pathlib.Path, temporary_run_directory: pathlib.Path, monkeypatch: pytest.MonkeyPatch
):
    """Test implicit bids_directory (cwd) with relative nwb_paths."""
    monkeypatch.chdir(temporary_run_directory)

    nwb_relative = minimal_nwbfile_path.relative_to(temporary_run_directory.parent)
    nwb_paths = [pathlib.Path("..") / nwb_relative]

    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths)
    assert not any(dataset_converter.notifications)

    expected_structure = {
        temporary_run_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_run_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_run_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_run_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_run_directory, expected_structure=expected_structure
    )
