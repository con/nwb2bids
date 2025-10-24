import pathlib
import typing

import pydantic

from .._converters._dataset_converter import DatasetConverter
from .._inspection._inspection_result import Category, InspectionResult, Severity


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    bids_directory: str | pathlib.Path | None = None,
    file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> list[InspectionResult]:
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
    notifications : list of InspectionResult
    """
    all_nwbfile_paths = []
    for nwb_path in nwb_paths:
        if nwb_path.is_file():
            all_nwbfile_paths.append(nwb_path)
        elif nwb_path.is_dir():
            all_nwbfile_paths += list(nwb_path.rglob(pattern="*.nwb"))

    if not all_nwbfile_paths:
        return [
            InspectionResult(
                title="No NWB Files Found",
                reason="No NWB files were found in the provided paths.",
                solution="Please provide paths that point to a NWB files or a directory containing NWB files.",
                category=Category.INTERNAL_ERROR,
                severity=Severity.CRITICAL,
            )
        ]

    converter = DatasetConverter.from_nwb_paths(
        nwb_paths=nwb_paths,
        additional_metadata_file_path=additional_metadata_file_path,
    )
    converter.extract_metadata()
    converter.convert_to_bids_dataset(bids_directory=bids_directory, file_mode=file_mode)

    return converter.messages
