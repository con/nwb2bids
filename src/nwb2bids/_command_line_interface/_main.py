import pathlib
import typing

import rich_click

from .._core._convert_nwb_dataset import convert_nwb_dataset
from ..sanitization import SanitizationLevel


# nwb2bids
@rich_click.group(name="nwb2bids")
def _nwb2bids_cli():
    pass


# nwb2bids convert [OPTIONS] [NWB_PATHS]...
@_nwb2bids_cli.command(name="convert")
@rich_click.argument("nwb_paths", type=str, nargs=-1)
@rich_click.option(
    "--bids-directory",
    "-o",
    help="Path to the folder where the BIDS dataset will be created (default: current working directory).",
    required=False,
    type=rich_click.Path(writable=True),
    default=None,
)
@rich_click.option(
    "--file-mode",
    help=(
        "How to handle the source NWB files when converting to BIDS format. "
        "By default, will attempt to utilize 'symlink' if the system allows. "
        "Otherwise, will 'copy' to preserve directory integrity. "
        "Use 'move' for fastest speeds if you do not wish to keep the original NWB directory structure."
    ),
    required=False,
    type=rich_click.Choice(["copy", "move", "symlink", "auto"], case_sensitive=False),
    default="auto",
)
@rich_click.option(
    "--additional-metadata-file-path",
    "additional_metadata_file_path",
    help=(
        "Path to a JSON file containing additional metadata to be included in the BIDS dataset. "
        "This file should contain a dictionary with keys corresponding to BIDS entities."
    ),
    required=False,
    type=rich_click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
)
@click.option(
    "--sanitization",
    help=("Specifies the level of sanitization to apply to file and directory names when creating the BIDS dataset."),
    required=False,
    type=click.Choice(["NONE", "0", "CRITICAL_BIDS_LABELS", "1"], case_sensitive=False),
    default="NONE",
)
@click.option("--silent", "-s", is_flag=True, help="Suppress all console output.", default=False)
def _run_convert_nwb_dataset(
    nwb_paths: tuple[str, ...],
    bids_directory: str | None = None,
    file_mode: typing.Literal["copy", "move", "symlink", "auto"] = "auto",
    additional_metadata_file_path: str | None = None,
    sanitization: typing.Literal["NONE", "0", "CRITICAL_BIDS_LABELS", "1"] = "NONE",
    silent: bool = False,
) -> None:
    """
    Convert NWB files to BIDS format.

    NWB_PATHS : A sequence of paths, each pointing to either an NWB file or a directory containing NWB files.
    """
    if len(nwb_paths) == 0:
        message = "Please provide at least one NWB file or directory to convert."
        raise ValueError(message)
    handled_nwb_paths = [pathlib.Path(nwb_path) for nwb_path in nwb_paths]
    handled_sanitization_level = (
        SanitizationLevel(int(sanitization)) if sanitization.isdigit() else getattr(SanitizationLevel, sanitization)
    )

    messages = convert_nwb_dataset(
        nwb_paths=handled_nwb_paths,
        bids_directory=bids_directory,
        file_mode=file_mode,
        additional_metadata_file_path=additional_metadata_file_path,
        sanitization_level=handled_sanitization_level,
    )

    if messages is not None and not silent:
        text = (
            f"{len(messages)} suggestion for improvement was found during conversion."
            if len(messages) == 1
            else f"{len(messages)} suggestions for improvement were found during conversion."
        )
        console_notification = rich_click.style(text=text, fg="yellow")
        rich_click.echo(message=console_notification)
