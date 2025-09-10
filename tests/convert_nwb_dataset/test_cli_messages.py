"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess


def test_minimal_cli_on_directory(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0
    assert b"3 suggestions for improvement were found during conversion." in result.stdout
    assert result.stderr == b""
