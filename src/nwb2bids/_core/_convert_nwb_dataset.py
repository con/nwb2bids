import pathlib
import typing

import pydantic

from .._converters._dataset_converter import DatasetConverter
from .._core._run_id import _generate_run_id
from ..sanitization import SanitizationLevel


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    bids_directory: str | pathlib.Path | None = None,
    file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    additional_metadata_file_path: pydantic.FilePath | None = None,
    sanitization_level: SanitizationLevel = SanitizationLevel.NONE,
    run_id: str | None = None,
) -> DatasetConverter:
    """
    Convert a dataset of NWB files to a BIDS dataset.

    Parameters
    ----------
    nwb_paths : any iterable of file or directory paths
        An iterable of NWB file paths and directories containing NWB files.
    bids_directory : string or path, optional
        The path to the directory where the BIDS dataset will be created.
        If None, uses the current working directory.
    file_mode : one of "move", "copy", "symlink", or "auto", default "auto"
        The file operation to use when adding files to the BIDS dataset.
        "move": Move the files (deletes the original files).
        "copy": Copy the files (original files remain unchanged).
        "symlink": Create symbolic links to the original files.
        "auto": Use "symlink" if the source and destination are on the same filesystem, otherwise use "copy".
    additional_metadata_file_path : file path, optional
        The path to a YAML file containing additional metadata not included within the NWB files
        that you wish to include in the BIDS dataset.
    sanitization_level : nwb2bids.SanitizationLevel
        Specifies the level of sanitization to apply to file and directory names when creating the BIDS dataset.
        Read more about the specific levels from `nwb2bids.sanitization.SanitizationLevel?`.
    run_id : str, optional
        On each unique run of nwb2bids, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the notification and sanitization reports saved to your cache directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."

    Returns
    -------
    converter : DatasetConverter
        The DatasetConverter used to perform the conversion.
        Contains notifications and other contextual information about the conversion process.
    """
    if run_id is None:
        run_id = _generate_run_id()

    converter = DatasetConverter.from_nwb_paths(
        nwb_paths=nwb_paths,
        additional_metadata_file_path=additional_metadata_file_path,
        run_id=run_id,
    )
    converter.extract_metadata()
    converter.convert_to_bids_dataset(
        bids_directory=bids_directory, file_mode=file_mode, sanitization_level=sanitization_level
    )

    return converter
