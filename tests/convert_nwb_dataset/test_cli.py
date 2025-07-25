"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess

import nwb2bids


def test_minimal_cli(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {minimal_nwbfile_path.parent} -o {temporary_bids_directory}"
    result = subprocess.run(args=command, check=True, shell=True)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": {"participants.json", "participants.tsv"}},
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


def test_ecephys_cli(ecephys_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {ecephys_nwbfile_path.parent} -o {temporary_bids_directory}"
    result = subprocess.run(args=command, check=True, shell=True)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": {"participants.json", "participants.tsv"}},
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
                "sub-123_ses-456_channels.tsv",
                "sub-123_ses-456_channels.json",
                "sub-123_ses-456_electrodes.tsv",
                "sub-123_ses-456_electrodes.json",
                "sub-123_ses-456_probes.tsv",
                "sub-123_ses-456_probes.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
