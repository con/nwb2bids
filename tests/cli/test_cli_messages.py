"""Integration tests for the primary `nwb2bids convert` CLI."""

import pathlib
import subprocess
from collections.abc import Callable

import pytest


@pytest.mark.container_cli_test
def test_problematic_cli_error_messages(
    problematic_nwbfile_path_1: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory}"

    result = cli_runner(command)
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
    ]
    actual_lines = result.stdout.decode(encoding="utf-8").splitlines()
    assert expected_message == actual_lines[:-2]
    assert "Please review the full notifications report at" in actual_lines[-2]
    assert b"No modality information found in session metadata" in result.stderr


@pytest.mark.container_cli_test
def test_problematic_cli_critical_messages(
    problematic_nwbfile_path_3: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {problematic_nwbfile_path_3} -o {temporary_bids_directory}"

    result = cli_runner(command)
    assert result.returncode == 0

    expected_message = ["", "BIDS dataset was successfully created, but may not be valid!", ""]
    actual_lines = result.stdout.decode(encoding="utf-8").splitlines()
    assert expected_message == actual_lines[:-2]
    assert "Please review the full notifications report at" in actual_lines[-2]
    assert b"No modality information found in session metadata" in result.stderr


@pytest.mark.container_cli_test
def test_problematic_cli_info_messages(
    problematic_nwbfile_path_4: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {problematic_nwbfile_path_4} -o {temporary_bids_directory}"

    result = cli_runner(command)
    assert result.returncode == 0

    expected_message = [
        "",
        "BIDS dataset was successfully created!",
        "1 suggestion for improvement was found during conversion.",
        "",
    ]
    actual_lines = result.stdout.decode(encoding="utf-8").splitlines()
    assert expected_message == actual_lines[:-2]
    assert "Please review the full notifications report at" in actual_lines[-2]
    assert result.stderr == b""


@pytest.mark.container_cli_test
def test_cli_success(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {minimal_nwbfile_path} -o {temporary_bids_directory}"

    result = cli_runner(command)
    assert result.returncode == 0

    expected_message = ["", "BIDS dataset was successfully created!", ""]
    actual_lines = result.stdout.decode(encoding="utf-8").splitlines()
    assert expected_message == actual_lines
    assert b"No modality information found in session metadata" in result.stderr


@pytest.mark.container_cli_test
def test_problematic_cli_silent(
    problematic_nwbfile_path_1: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert {problematic_nwbfile_path_1} -o {temporary_bids_directory} --silent"

    result = cli_runner(command)
    assert result.returncode == 0
    assert result.stdout == b""
    assert result.stderr == b""
