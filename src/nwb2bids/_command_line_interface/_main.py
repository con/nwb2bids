import pathlib
import typing

import click

from .._core._convert_nwb_dataset import convert_nwb_dataset


# nwb2bids
@click.group(name="nwb2bids")
def _nwb2bids_cli():
    pass


# nwb2bids convert [OPTIONS] [NWB_PATHS]...
@_nwb2bids_cli.command(name="convert")
@click.argument("nwb_paths", type=str, nargs=-1)
@click.option(
    "--bids-directory",
    "-o",
    help="Path to the folder where the BIDS dataset will be created (default: current working directory).",
    required=False,
    type=click.Path(writable=True),
    default=None,
)
@click.option(
    "--file-mode",
    help=(
        "How to handle the source NWB files when converting to BIDS format. "
        "By default, will attempt to utilize 'symlink' if the system allows. "
        "Otherwise, will 'copy' to preserve directory integrity. "
        "Use 'move' for fastest speeds if you do not wish to keep the original NWB directory structure."
    ),
    required=False,
    type=click.Choice(["copy", "move", "symlink", "auto"], case_sensitive=False),
    default="auto",
)
@click.option(
    "--additional-metadata-file-path",
    "additional_metadata_file_path",
    help=(
        "Path to a JSON file containing additional metadata to be included in the BIDS dataset. "
        "This file should contain a dictionary with keys corresponding to BIDS entities."
    ),
    required=False,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
)
@click.option("--silent", "-s", is_flag=True, help="Suppress all console output.", default=False)
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

    messages = convert_nwb_dataset(
        nwb_paths=handled_nwb_paths,
        bids_directory=bids_directory,
        file_mode=file_mode,
        additional_metadata_file_path=additional_metadata_file_path,
    )

    if len(messages) > 0 and not silent:
        text = (
            f"\n{len(messages)} suggestion for improvement was found during conversion."
            if len(messages) == 1
            else f"{len(messages)} suggestions for improvement were found during conversion."
        )
        console_notification = click.style(text=text, fg="yellow")
        click.echo(message=console_notification)
