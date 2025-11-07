import pathlib
import typing

import rich_click

from .._core._convert_nwb_dataset import convert_nwb_dataset
from .._inspection._inspection_result import Severity
from .._tools._pluralize import _pluralize
from ..testing import generate_ephys_tutorial


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
@rich_click.option("--silent", "-s", is_flag=True, help="Suppress all console output.", default=False)
def _run_convert_nwb_dataset(
    nwb_paths: tuple[str, ...],
    bids_directory: str | None = None,
    file_mode: typing.Literal["copy", "move", "symlink", "auto"] = "auto",
    additional_metadata_file_path: str | None = None,
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

    notifications = convert_nwb_dataset(
        nwb_paths=handled_nwb_paths,
        bids_directory=bids_directory,
        file_mode=file_mode,
        additional_metadata_file_path=additional_metadata_file_path,
    )

    if notifications and not silent:
        text = (
            f'\n{(n:=len(notifications))} {_pluralize(n=n, word="suggestion")} for improvement '
            f'{_pluralize(n=n, word="was", plural="were")} found during conversion.'
        )
        console_notification = rich_click.style(text=text, fg="yellow")
        rich_click.echo(message=console_notification)

    not_any_failures = not messages or not any(message.severity == Severity.ERROR for message in messages)
    if not_any_failures and not silent:
        text = "\nBIDS dataset was successfully created!\n\n"
        console_notification = rich_click.style(text=text, fg="green")
        rich_click.echo(message=console_notification)


# nwb2bids tutorial
@_nwb2bids_cli.group(name="tutorial")
def _nwb2bids_tutorial_cli():
    pass


# nwb2bids tutorial ephys
@_nwb2bids_tutorial_cli.group(name="ephys")
def _nwb2bids_tutorial_ephys_cli():
    pass


# nwb2bids tutorial ephys file
@_nwb2bids_tutorial_ephys_cli.command(name="file")
@rich_click.option(
    "--output-directory",
    "-o",
    help="Path to the folder where the tutorial file(s) will be created (default: user home directory).",
    required=False,
    type=rich_click.Path(writable=True),
    default=None,
)
def _nwb2bids_tutorial_ephys_file_cli(output_directory: str | None = None) -> None:
    file_path = generate_ephys_tutorial(output_directory=output_directory, mode="file")

    text = f"\nAn example NWB file has been created at: {file_path}\n\n"
    message = rich_click.style(text=text, fg="green")
    rich_click.echo(message=message)


# nwb2bids tutorial ephys dataset
@_nwb2bids_tutorial_ephys_cli.command(name="dataset")
@rich_click.option(
    "--output-directory",
    "-o",
    help="Path to the folder where the tutorial files will be created (default: user home directory).",
    required=False,
    type=rich_click.Path(writable=True),
    default=None,
)
def _nwb2bids_tutorial_ephys_dataset_cli(output_directory: str | None = None) -> None:
    tutorial_directory = generate_ephys_tutorial(output_directory=output_directory, mode="dataset")

    text = f"\nAn example NWB dataset has been created at: {tutorial_directory}\n\n"
    message = rich_click.style(text=text, fg="green")
    rich_click.echo(message=message)
