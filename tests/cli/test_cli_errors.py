import pathlib
import subprocess
from collections.abc import Callable

import pytest


@pytest.mark.container_cli_test
def test_cli_without_arg(
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
):
    command = f"nwb2bids convert -o {temporary_bids_directory}"

    result = cli_runner(command)
    assert result.returncode == 1
    assert result.stdout == b""
    assert b"Please provide at least one NWB file or directory to convert." in result.stderr
