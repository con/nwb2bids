"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess
from collections.abc import Callable

import pytest

import nwb2bids


@pytest.mark.container_cli_test
def test_minimal_cli_on_directory(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {minimal_nwbfile_path.parent} -o {temporary_bids_directory}"

    result = cli_runner(command)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

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


@pytest.mark.container_cli_test
def test_minimal_cli_on_file_path(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert --bids-directory {temporary_bids_directory} {minimal_nwbfile_path}"

    result = cli_runner(command)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

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


@pytest.mark.container_cli_test
def test_ecephys_cli(
    ecephys_tutorial_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {ecephys_tutorial_nwbfile_path.parent} -o {temporary_bids_directory}"
    result = cli_runner(command)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

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


@pytest.mark.container_cli_test
def test_minimal_cli_on_file_paths(
    directory_with_multiple_nwbfiles: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert -o {temporary_bids_directory} {directory_with_multiple_nwbfiles}/*.nwb"
    result = cli_runner(command)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-session-0", "ses-session-1"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-0": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-0"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-123_ses-session-0_ecephys.nwb",
            },
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-1": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-1"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-123_ses-session-1_ecephys.nwb",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
