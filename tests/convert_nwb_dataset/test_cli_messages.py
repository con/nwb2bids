"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess


def test_problematic_cli_error_messages(
    problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0

    expected_message = [
        "",
        "BIDS dataset was not successfully created!",
        "Some errors were encountered during conversion.",
        "The first 3 of 4 are shown below:",
        "",
        "",
        "\t- Participant species is not a proper Latin binomial or NCBI Taxonomy id.",
        "\t- The participant ID contains invalid characters. BIDS allows only the "
        "plus sign to be used as a separator in the subject entity label. "
        "Underscores, dashes, spaces, slashes, and other special characters "
        "(including #) are expressly forbidden.",
        "\t- Participant sex is not one of the allowed patterns by BIDS.",
        "",
        "",
    ]
    assert expected_message == result.stdout.decode(encoding="utf-8").splitlines()
    assert result.stderr == b""


def test_problematic_cli_critical_messages(
    problematic_nwbfile_path_3: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    command = f"nwb2bids convert {problematic_nwbfile_path_3} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0

    expected_message = ["", "BIDS dataset was successfully created, but may not be valid!", ""]
    assert expected_message == result.stdout.decode(encoding="utf-8").splitlines()
    assert result.stderr == b""


def test_problematic_cli_info_messages(
    problematic_nwbfile_path_4: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    command = f"nwb2bids convert {problematic_nwbfile_path_4} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0

    expected_message = ["", "BIDS dataset was successfully created, but may not be valid!", ""]
    assert expected_message == result.stdout.decode(encoding="utf-8").splitlines()
    assert result.stderr == b""


def test_problematic_cli_success(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {minimal_nwbfile_path} -o {temporary_bids_directory}"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0

    expected_message = ["", "BIDS dataset was successfully created!", "", ""]
    assert expected_message == result.stdout.decode(encoding="utf-8").splitlines()
    assert result.stderr == b""


def test_problematic_cli_silent(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory} --silent"

    result = subprocess.run(args=command, shell=True, capture_output=True)
    assert result.returncode == 0
    assert result.stdout == b""
    assert result.stderr == b""
