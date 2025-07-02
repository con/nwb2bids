import pathlib
import typing

import pydantic

from ._dataset_converter import DatasetConverter


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_directory: pydantic.DirectoryPath,
    bids_directory: str | pathlib.Path,
    copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink",
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> None:
    converter = DatasetConverter(
        nwb_directory=nwb_directory, additional_metadata_file_path=additional_metadata_file_path
    )
    converter.extract_dataset_metadata()
    converter.convert_to_bids_dataset(bids_directory=bids_directory, copy_mode=copy_mode)
