import click


# nwb2bids < nwb_directory > < bids_directory >
@click.command(name="nwb2bids")
@click.argument("nwb_directory", type=click.Path(writable=False))
@click.argument("bids_directory", type=click.Path(writable=True))
@click.option(
    "--copy",
    help=("Whether or not to copy data from the NWB files into the BIDS format. " "Otherwise, files will be moved."),
    required=False,
    type=click.BOOL,
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
def _run_nwb2bids(
    nwb_directory: str,
    bids_directory: str,
    copy: bool = True,
    additional_metadata_file_path: str | None = None,
) -> None:
    """
    Convert NWB files to BIDS format.

    NWB_DIRECTORY : The path to the folder containing NWB files.
    BIDS_DIRECTORY : The path to the folder where the BIDS dataset will be created.
    """
    pass
