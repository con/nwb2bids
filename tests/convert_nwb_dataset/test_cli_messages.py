"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess


def test_problematic_cli_messages(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0
    assert b"4 suggestions for improvement were found during conversion." in result.stdout.strip()
    assert result.stderr == b""


def test_problematic_cli_silent(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory} --silent"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0
    assert result.stdout == b""
    assert result.stderr == b""
