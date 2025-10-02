"""Sanitization tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess

import nwb2bids


def test_cli_level_1_sanitization(problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {problematic_nwbfile_path_2.parent} --output {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
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
