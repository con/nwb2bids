import typing

import click

from .._base._convert_nwb_dataset import convert_nwb_dataset


# nwb2bids
@click.group(name="nwb2bids")
def _nwb2bids_cli():
    pass


# nwb2bids convert < nwb_directory > < bids_directory >
@_nwb2bids_cli.command(name="convert")
@click.argument("nwb_directory", type=click.Path(writable=False))
@click.option(
    "--bids-directory",
    "-o",
    help="The path to the folder where the BIDS dataset will be created.",
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
    type=click.Choice(["copy", "move", "symlink"], case_sensitive=False),
    default=None,
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
def _run_convert_nwb_dataset(
    nwb_directory: str,
    bids_directory: str | None = None,
    file_mode: typing.Literal["copy", "move", "symlink"] | None = None,
    additional_metadata_file_path: str | None = None,
) -> None:
    """
    Convert NWB files to BIDS format.

    NWB_DIRECTORY : The path to the folder containing NWB files.
    """
    convert_nwb_dataset(
        nwb_directory=nwb_directory,
        bids_directory=bids_directory,
        file_mode=file_mode,
        additional_metadata_file_path=additional_metadata_file_path,
    )
