import typing
import warnings

import click

from .._base import convert_nwb_dataset


# nwb2bids
@click.group(name="nwb2bids")
def _nwb2bids_cli():
    pass


# TODO: remove
# nwb2bids reposit < nwb_directory > < bids_directory >
@_nwb2bids_cli.command(name="reposit", deprecated=True)
@click.argument("nwb_directory", type=click.Path(writable=False))
@click.argument("bids_directory", type=click.Path(writable=True))
@click.option(
    "--no-copy",
    help="Whether or not to copy data from the NWB files into the BIDS format. Otherwise, files will be moved.",
    required=False,
    type=click.BOOL,
    default=False,
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
    bids_directory: str,
    no_copy: bool = False,
    additional_metadata_file_path: str | None = None,
) -> None:
    message = (
        "The `nwb2bids reposit` CLI is deprecated and will be removed in a future release. "
        "Please use `nwb2bids convert` instead.",
    )
    warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

    convert_nwb_dataset(
        nwb_directory=nwb_directory,
        bids_directory=bids_directory,
        file_mode="move" if no_copy is True else "copy",
        additional_metadata_file_path=additional_metadata_file_path,
    )


# nwb2bids convert < nwb_directory > < bids_directory >
@_nwb2bids_cli.command(name="convert")
@click.argument("nwb_directory", type=click.Path(writable=False))
@click.argument("bids_directory", type=click.Path(writable=True))
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
    default=True,
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
    bids_directory: str,
    file_mode: typing.Literal["copy", "move", "symlink"] | None = None,
    additional_metadata_file_path: str | None = None,
) -> None:
    """
    Convert NWB files to BIDS format.

    NWB_DIRECTORY : The path to the folder containing NWB files.
    BIDS_DIRECTORY : The path to the folder where the BIDS dataset will be created.
    """
    convert_nwb_dataset(
        nwb_directory=nwb_directory,
        bids_directory=bids_directory,
        file_mode=file_mode,
        additional_metadata_file_path=additional_metadata_file_path,
    )
