"""Pytest configuration for CLI integration tests."""

import os
import subprocess
from collections.abc import Callable

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--container-image",
        action="store",
        default=None,
        help="Docker/container image to test CLI against (e.g., nwb2bids:dev)",
    )


def pytest_report_header(config: pytest.Config) -> str | None:
    image = config.getoption("--container-image")
    if image:
        return f"container image: {image}"
    return None


@pytest.fixture(scope="session")
def container_image(request: pytest.FixtureRequest) -> str | None:
    """Returns the container image specified via --container-image, or None."""
    return request.config.getoption("--container-image")


@pytest.fixture(scope="session")
def cli_runner(
    tmp_path_factory: pytest.TempPathFactory,
    container_image: str | None,
) -> Callable[[str], subprocess.CompletedProcess]:
    """
    Returns a function to run CLI commands.

    If --container-image is specified, commands run inside the container
    with the pytest temp directory bind-mounted.
    """
    basetemp = tmp_path_factory.getbasetemp()

    if container_image:
        uid, gid = os.getuid(), os.getgid()
        # Set HOME to basetemp so ~/.cache and ~/.nwb2bids resolve to writable locations
        prefix = (
            f"docker run --rm --user {uid}:{gid} "
            f"-v {basetemp}:{basetemp} "
            f"-e HOME={basetemp} "
            f"{container_image}"
        )
    else:
        prefix = ""

    def run(command: str) -> subprocess.CompletedProcess:
        full_command = f"{prefix} {command}" if prefix else command
        return subprocess.run(args=full_command, shell=True, capture_output=True)

    return run
