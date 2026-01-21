"""Sanitization tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess
from collections.abc import Callable

import pytest

import nwb2bids


@pytest.mark.container_cli_test
def test_cli_basic_sanitization(
    problematic_nwbfile_path_2: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = (
        f"nwb2bids convert {problematic_nwbfile_path_2} -o {temporary_bids_directory} "
        "--sanitization sub-labels --sanitization ses-labels"
    )

    result = cli_runner(command)
    assert (
        result.returncode == 0
    ), f"\n\nCLI command failed with:\nStandard Output: {result.stdout}\nStandard Error: {result.stderr}\n\n"

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-bad+subject+id"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-bad+subject+id": {
            "directories": {"ses-problematic+2"},
            "files": {"sub-bad+subject+id_sessions.json", "sub-bad+subject+id_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-bad+subject+id"
        / "ses-problematic+2": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-bad+subject+id"
        / "ses-problematic+2"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-bad+subject+id_ses-problematic+2_ecephys.nwb",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
