import collections
import pathlib
import typing

import pydantic

from ._loading import _load_and_validate_additional_metadata
from ._session_converter import SessionConverter
from ._writing import _write_dataset_description, _write_sessions_info, _write_subjects_info
from ..schemas import BidsDatasetMetadata


class DatasetConverter(pydantic.BaseModel):
    def __init__(
        self, nwb_directory: pydantic.DirectoryPath, additional_metadata_file_path: pydantic.FilePath | None = None
    ) -> None:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_directory : directory path
            The path to the directory containing NWB files.
        additional_metadata_file_path : file path, optional
            The path to a JSON file containing additional metadata to be included in the BIDS dataset.
            If not provided, the method will also look for a file named "additional_metadata.json" in the NWB directory.
        """
        super().__init__()

        self.nwb_directory = pathlib.Path(nwb_directory)
        self.nwb_file_paths: list[pathlib.Path] = list(self.nwb_directory.rglob(pattern="*.nwb"))
        self.session_converters: list[SessionConverter] = [
            SessionConverter(nwb_file_path=nwb_file_path) for nwb_file_path in self.nwb_file_paths
        ]

        self.dataset_metadata: BidsDatasetMetadata | None = None
        self.additional_metadata: BidsDatasetMetadata | None = None
        additional_metadata_file_path = (
            secondary_path
            if additional_metadata_file_path is None
            and (secondary_path := pathlib.Path(nwb_directory) / "additional_metadata.json").exists()
            else additional_metadata_file_path
        )
        if additional_metadata_file_path is not None:
            self.additional_metadata = _load_and_validate_additional_metadata(file_path=additional_metadata_file_path)

    def extract_dataset_metadata(self) -> None:
        """
        Extract metadata from the NWB files across the specified directory and set it to an internal attribute.
        """
        collections.deque(
            (
                session_converter.extract_session_metadata()
                for session_converter in self.session_converters
                if session_converter.session_metadata is None
            ),
            maxlen=0,
        )
        self.dataset_metadata = [session_converter.metadata for session_converter in self.session_converters]

    def convert_to_bids_dataset(
        self, bids_directory: str | pathlib.Path, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink"
    ) -> None:
        """
        Convert the directory of NWB files to a BIDS dataset.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        copy_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
        """
        bids_directory = pathlib.Path(bids_directory)
        bids_directory.mkdir(exist_ok=True)

        if self.dataset_metadata is None:
            self.extract_dataset_metadata()

        if self.additional_metadata is not None:
            _write_dataset_description(additional_metadata=self.additional_metadata, bids_directory=bids_directory)

        _write_subjects_info(all_metadata=self.dataset_metadata, bids_directory=bids_directory)
        _write_sessions_info(subjects=self.dataset_metadata, bids_directory=bids_directory)

        collections.deque(
            (
                session_converter.convert_to_bids_session(bids_directory=bids_directory, copy_mode=copy_mode)
                for session_converter in self.session_converters
            ),
            maxlen=0,
        )
