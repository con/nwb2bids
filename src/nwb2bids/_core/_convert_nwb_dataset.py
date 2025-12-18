import os
import pathlib
import typing

import pydantic

from .._converters._dataset_converter import DatasetConverter
from .._converters._run_config import RunConfig


def _make_absolute(p: pathlib.Path) -> pathlib.Path:
    """Make path absolute and normalized without following symlinks.

    Uses os.path.abspath for normalization because:
    - pathlib.resolve() follows symlinks (breaks git-annex/datalad paths)
    - pathlib.absolute() doesn't normalize '..' components
    - os.path.abspath normalizes without following symlinks
    """
    return pathlib.Path(os.path.abspath(p))


AbsoluteFilePath = typing.Annotated[pydantic.FilePath, pydantic.BeforeValidator(_make_absolute)]
AbsoluteDirectoryPath = typing.Annotated[pydantic.DirectoryPath, pydantic.BeforeValidator(_make_absolute)]


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: list[AbsoluteFilePath | AbsoluteDirectoryPath] = pydantic.Field(min_length=1),
    run_config: RunConfig = pydantic.Field(default_factory=RunConfig),
) -> DatasetConverter:
    """
    Convert a dataset of NWB files to a BIDS dataset.

    Parameters
    ----------
    nwb_paths : any iterable of file or directory paths
        An iterable of NWB file paths and directories containing NWB files.
    run_config : RunConfig, optional
        The configuration for this conversion run.

    Returns
    -------
    converter : DatasetConverter
        The DatasetConverter used to perform the conversion.
        Contains notifications and other contextual information about the conversion process.
    """
    converter = DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    converter.extract_metadata()
    converter.convert_to_bids_dataset()

    return converter
