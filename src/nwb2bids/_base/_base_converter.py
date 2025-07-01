import abc
import pathlib
import typing

import pydantic

from ._additional_metadata import _load_and_validate_additional_metadata
from ..schemas import BidsDatasetMetadata


class BaseConverter(pydantic.BaseModel, abc.ABC):
    nwb_directory: pydantic.DirectoryPath
    bids_directory: str | pathlib.Path
    additional_metadata_file_path: pydantic.FilePath | None = pydantic.Field(
        description="An additional source of custom metadata to use when creating the BIDS dataset.", default=None
    )

    def __init__(
        self,
        nwb_directory: pydantic.DirectoryPath,
        bids_directory: str | pathlib.Path,
        additional_metadata_file_path: pydantic.FilePath | None = None,
    ) -> None:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_directory : directory path
            The path to the directory containing NWB files.
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        additional_metadata_file_path : file path, optional
            The path to a JSON file containing additional metadata to be included in the BIDS dataset.
            If not provided, the method will also look for a file named "additional_metadata.json" in the NWB directory.
        """
        self.nwb_directory = pathlib.Path(bids_directory)
        self.bids_directory = pathlib.Path(bids_directory)

        self.additional_metadata = None
        additional_metadata_file_path = (
            secondary_path
            if additional_metadata_file_path is None
            and (secondary_path := pathlib.Path(nwb_directory) / "additional_metadata.json").exists()
            else additional_metadata_file_path
        )
        if additional_metadata_file_path is not None:
            self.additional_metadata = _load_and_validate_additional_metadata(file_path=additional_metadata_file_path)

    @abc.abstractmethod
    def extract_metadata(self) -> BidsDatasetMetadata:
        """
        Extract metadata from the NWB files across the specified directory.
        """
        message = "This method should be implemented in a subclass."
        raise NotImplementedError(message)

    @abc.abstractmethod
    def convert_to_bids(self, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink") -> None:
        """
        Convert the directory of NWB files to a BIDS dataset.

        Parameters
        ----------
        copy_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
        """
        message = "This method should be implemented in a subclass."
        raise NotImplementedError(message)
