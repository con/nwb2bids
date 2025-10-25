import pydantic

from .._converters._dataset_converter import DatasetConverter
from .._converters._run_config import RunConfig


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    run_config: RunConfig = pydantic.Field(default_factory=RunConfig),
) -> DatasetConverter:
    """
    Convert a dataset of NWB files to a BIDS dataset.

    Parameters
    ----------
    nwb_paths : any iterable of file or directory paths
        An iterable of NWB file paths and directories containing NWB files.


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
