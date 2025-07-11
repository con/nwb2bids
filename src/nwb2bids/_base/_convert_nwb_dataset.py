import pathlib
import typing

import pydantic

from nwb2bids._converters._dataset_converter import DatasetConverter


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_directory: pydantic.DirectoryPath,
    bids_directory: str | pathlib.Path,
    file_mode: typing.Literal["move", "copy", "symlink"] | None = None,
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> None:
    converter = DatasetConverter.from_nwb_directory(
        nwb_directory=nwb_directory, additional_metadata_file_path=additional_metadata_file_path
    )
    converter.extract_dataset_metadata()
    converter.convert_to_bids_dataset(bids_directory=bids_directory, file_mode=file_mode)
