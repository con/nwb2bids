import datetime
import json
import pathlib
import typing

import pydantic

from .._converters._dataset_converter import DatasetConverter
from .._inspection._inspection_result import InspectionResult


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    bids_directory: str | pathlib.Path | None = None,
    file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> tuple[list[InspectionResult], pathlib.Path]:
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

    Returns
    -------
    notifications : list of InspectionResult or None
        A list of inspection results, or None if there are no internal messages.
    log_file_path : pathlib.Path
        The path to the log file where the notifications have been recorded.
    """
    converter = DatasetConverter.from_nwb_paths(
        nwb_paths=nwb_paths,
        additional_metadata_file_path=additional_metadata_file_path,
    )
    converter.extract_metadata()
    converter.convert_to_bids_dataset(bids_directory=bids_directory, file_mode=file_mode)

    home_dir = pathlib.Path.home() / ".nwb2bids"
    home_dir.mkdir(exist_ok=True)
    log_dir = home_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file_path = log_dir / f"{datetime.datetime.now()}.json"
    notifications_dump = [notification.model_dump(mode="json") for notification in converter.messages]
    if len(notifications_dump) > 0:
        log_file_path.write_text(data=json.dumps(obj=notifications_dump, indent=2))

    return converter.messages, log_file_path
