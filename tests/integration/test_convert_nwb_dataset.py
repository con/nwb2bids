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
            "ExampleProbe\tn/a\t`nwb2bids` test suite\tThis is an example ecephys probe "
            "used for demonstration purposes."
        ),
    ]
    assert probes_tsv_lines == expected_probe_tsv_lines

    probes_json_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_probes.json"
    probes_json = json.loads(probes_json_file_path.read_text())
    expected_probes_json = {
        "description": {"Description": "Probe description from NWB file.", "LongName": "Description"},
        "manufacturer": {
            "Description": "Manufacturer of the probes system (for "
            "example, 'openephys', "
            "'alphaomega','blackrock').",
            "LongName": "Manufacturer",
        },
        "probe_name": {
            "Description": "A unique identifier of the probe, can be " "identical with the device_serial_number.",
            "LongName": "Probe name",
        },
        "type": {"Description": "The type of the probe.", "LongName": "Type"},
    }
    assert probes_json == expected_probes_json

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

    electrodes_json_file_path = (
        temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.json"
    )
    electrodes_json = json.loads(electrodes_json_file_path.read_text())
    expected_electrodes_json = {
        "hemisphere": {
            "Description": "The hemisphere in which the electrode is " "placed.",
            "Levels": {"L": "left", "R": "right"},
            "LongName": "Hemisphere",
        },
        "impedance": {"Description": "Impedance of the electrode, units MUST be in " "kOhm.", "LongName": "Impedance"},
        "location": {
            "Description": "An indication on the location of the electrode " "(for example, cortical layer 3, CA1).",
            "LongName": "Location",
        },
        "name": {"Description": "Name of the electrode contact point.", "LongName": "Electrode name"},
        "probe_name": {
            "Description": "A unique identifier of the probe, can be "
            "identical with the device_serial_number. The "
            "value MUST match a probe_name entry in the "
            "corresponding *_probes.tsv file, linking this "
            "electrode to its associated probe. For "
            "electrodes not associated with a probe, use "
            "n/a.",
            "LongName": "Probe name",
        },
        "shank_id": {
            "Description": "A unique identifier to specify which shank of "
            "the probe the electrode is on. This is useful "
            "for spike sorting when the electrodes are on a "
            "multi-shank probe.",
            "LongName": "Shank ID",
        },
        "x": {
            "Description": "Recorded position along the x-axis. When no "
            "space-<label> entity is used in the filename, the "
            "position along the local width-axis relative to the "
            "probe origin (see coordinate_reference_point in "
            "*_probes.tsv) in micrometers (um). When a space-<label> "
            "entity is used in the filename, the position relative "
            "to the origin of the coordinate system along the first "
            "axis. Units are specified by MicroephysCoordinateUnits "
            "in the corresponding *_coordsystem.json file.",
            "LongName": "x",
        },
        "y": {
            "Description": "Recorded position along the y-axis. When no "
            "space-<label> entity is used in the filename, the "
            "position along the local height-axis relative to the "
            "probe origin (see coordinate_reference_point in "
            "*_probes.tsv) in micrometers (um). When a space-<label> "
            "entity is used in the filename, the position relative "
            "to the origin of the coordinate system along the second "
            "axis. Units are specified by MicroephysCoordinateUnits "
            "in the corresponding *_coordsystem.json file.",
            "LongName": "y",
        },
        "z": {
            "Description": "Recorded position along the z-axis. For 2D electrode "
            "localizations, this SHOULD be a column of n/a values. "
            "When no space-<label> entity is used in the filename, "
            "the position along the local depth-axis relative to the "
            "probe origin (see coordinate_reference_point in "
            "*_probes.tsv) in micrometers (um). When a space-<label> "
            "entity is used in the filename, the position relative "
            "to the origin of the coordinate system along the third "
            "axis. Units are specified by MicroephysCoordinateUnits "
            "in the corresponding *_coordsystem.json file. For 2D "
            "electrode localizations (for example, when the "
            "coordinate system is Pixels), this SHOULD be a column "
            "of n/a values.",
            "LongName": "z",
        },
    }
    assert electrodes_json == expected_electrodes_json

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

    channels_json_file_path = temporary_bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.json"
    channels_json = json.loads(channels_json_file_path.read_text())
    expected_channels_json = {
        "electrode_name": {
            "Description": "Name of the electrode contact point. The "
            "value MUST match a name entry in the "
            "corresponding *_electrodes.tsv file, "
            "linking this channel to its associated "
            "electrode contact point. For channels not "
            "associated with an electrode, use n/a.",
            "LongName": "Electrode name",
        },
        "gain": {
            "Description": "Amplification factor applied from signal detection "
            "at the electrode to the signal stored in the data "
            "file. If no gain factor is provided it is assumed to "
            "be 1.",
            "LongName": "Gain",
        },
        "name": {"Description": "Label of the channel.", "LongName": "Channel name"},
        "sampling_frequency": {"Description": "Sampling rate of the channel in Hz.", "LongName": "Sampling frequency"},
        "stream_id": {"Description": "Data stream of the recording the signal.", "LongName": "Stream ID"},
        "type": {
            "Description": "Type of channel; MUST use the channel types listed "
            "below. Note that the type MUST be in upper-case.",
            "LongName": "Type",
        },
        "units": {
            "Description": "Physical unit of the value represented in this "
            "channel, for example, V for Volt, or fT/cm for "
            "femto Tesla per centimeter (see Units).",
            "LongName": "Units",
        },
    }
    assert channels_json == expected_channels_json


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
