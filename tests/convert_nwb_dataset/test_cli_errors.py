import pathlib
import subprocess


def test_cli_without_arg(temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 1
    assert result.stdout == b""
    assert b"Please provide at least one NWB file or directory to convert." in result.stderr
