import pathlib
import typing

import rich_click

from .._converters._run_config import RunConfig
from .._core._convert_nwb_dataset import convert_nwb_dataset
from .._tools._pluralize import _pluralize


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
    "--cache-directory",
    "cache_directory",
    help=(
        "The directory where run specific files (e.g., notifications, sanitization reports) will be stored. "
        "Defaults to `~/.nwb2bids`."
    ),
    required=False,
    type=rich_click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
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
@rich_click.option(
    "--run-id",
    help=(
        "On each unique run of nwb2bids, a run ID is generated. "
        "Set this option to override this to any identifying string. "
        "This ID is used in the naming of the notification and sanitization reports saved to your cache directory. "
        'The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."'
    ),
    required=False,
    type=str,
    default=None,
)
def _run_convert_nwb_dataset(
    nwb_paths: tuple[str, ...],
    bids_directory: str | None = None,
    additional_metadata_file_path: str | None = None,
    file_mode: typing.Literal["copy", "move", "symlink", "auto"] = "auto",
    cache_directory: str | None = None,
    run_id: str | None = None,
    silent: bool = False,
) -> None:
    """
    Convert NWB files to BIDS format.

    NWB_PATHS : A space-separated sequence of paths, each pointing to either an NWB file
    or a directory containing NWB files.
    """
    if len(nwb_paths) == 0:
        message = "Please provide at least one NWB file or directory to convert."
        raise ValueError(message)
    handled_nwb_paths = [pathlib.Path(nwb_path) for nwb_path in nwb_paths]

    run_config_kwargs = {
        "bids_directory": bids_directory,
        "additional_metadata_file_path": additional_metadata_file_path,
        "file_mode": file_mode,
        "cache_directory": cache_directory,
        "run_id": run_id,
    }

    # Filter out values that indicate absence of direct user input or signal to use default
    non_missing_run_config_kwargs = {
        key: value
        for key, value in run_config_kwargs.items()
        if (key != "file_mode" and value is not None) or (key == "file_mode" and value != "auto")
    }
    run_config = RunConfig(**non_missing_run_config_kwargs)

    converter = convert_nwb_dataset(nwb_paths=handled_nwb_paths, run_config=run_config)

    notifications = converter.messages
    console_notification = ""
    if notifications:
        notification_text = (
            f'\n{(n:=len(notifications))} {_pluralize(n=n, word="suggestion")} for improvement '
            f'{_pluralize(n=n, word="was", plural="were")} found during conversion.'
        )
        console_notification += rich_click.style(text=notification_text, fg="yellow")

    if console_notification != "" and not silent:
        rich_click.echo(message=console_notification)
