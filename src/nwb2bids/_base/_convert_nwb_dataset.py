import pathlib
import typing

import pydantic

from .._converters._dataset_converter import DatasetConverter


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_paths: typing.Iterable[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    bids_directory: str | pathlib.Path | None = None,
    file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> None:
    converter = DatasetConverter.from_nwb_paths(
        nwb_paths=nwb_paths,
        additional_metadata_file_path=additional_metadata_file_path,
    )
    converter.extract_metadata()
    converter.convert_to_bids_dataset(bids_directory=bids_directory, file_mode=file_mode)
