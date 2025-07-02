import collections
import json
import pathlib
import typing

import pandas
import pydantic

from ._session_converter import SessionConverter
from ._writing import _write_dataset_description, _write_sessions_info
from ..models import BidsDatasetMetadata


class DatasetConverter(pydantic.BaseModel):
    session_converters: list[SessionConverter]
    dataset_metadata: BidsDatasetMetadata | None = None

    @classmethod
    @pydantic.validate_call
    def from_nwb_directory(
        cls, nwb_directory: pydantic.DirectoryPath, additional_metadata_file_path: pydantic.FilePath | None = None
    ) -> typing.Self:
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
        session_converters = SessionConverter.from_nwb_directory(nwb_directory=nwb_directory)

        dataset_metadata = None
        additional_metadata_file_path = (
            secondary_path
            if additional_metadata_file_path is None
            and (secondary_path := nwb_directory / "additional_metadata.json").exists()
            else additional_metadata_file_path
        )
        if additional_metadata_file_path is not None:
            dataset_metadata = BidsDatasetMetadata.from_file_path(file_path=additional_metadata_file_path)

        dataset_converter = cls(session_converters=session_converters, dataset_metadata=dataset_metadata)
        return dataset_converter

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

        sessions_metadata = [session_converter.session_metadata for session_converter in self.session_converters]
        self.dataset_metadata = BidsDatasetMetadata(sessions_metadata=sessions_metadata)

    @pydantic.validate_call
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
        bids_directory.mkdir(exist_ok=True)
        if self.dataset_metadata is None:
            self.extract_dataset_metadata()

        if self.additional_metadata is not None:
            _write_dataset_description(additional_metadata=self.additional_metadata, bids_directory=bids_directory)

        self.write_participants_metadata(bids_directory=bids_directory)
        _write_sessions_info(subjects=self.dataset_metadata, bids_directory=bids_directory)

        collections.deque(
            (
                session_converter.convert_to_bids_session(bids_directory=bids_directory, copy_mode=copy_mode)
                for session_converter in self.session_converters
            ),
            maxlen=0,
        )

    @pydantic.validate_call
    def write_participants_metadata(self, bids_directory: str | pathlib.Path) -> None:
        """
        Write the `participants.tsv`, `participants.json`, and create empty subject directories.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        bids_directory.mkdir(exist_ok=True)
        if self.dataset_metadata is None:
            self.extract_dataset_metadata()

        participants_data_frame = pandas.DataFrame.from_records(
            data=[
                {key: value for key, value in session_metadata.subject.model_dump().items() if value is not None}
                for session_metadata in self.dataset_metadata.sessions_metadata
            ]
        ).astype("string")
        is_field_in_table = {field: True for field in participants_data_frame.keys()}

        # BIDS validation is strict about order
        column_order = ("participant_id", "species", "sex", "strain")
        participants_data_frame = participants_data_frame.reindex(
            columns=tuple(field for field in column_order if is_field_in_table.get(field, False) is True)
        )

        participants_tsv_file_path = bids_directory / "participants.tsv"
        participants_data_frame.to_csv(path_or_buf=participants_tsv_file_path, mode="w", index=False, sep="\t")

        is_field_in_table = {field: True for field in participants_data_frame.keys()}
        participants_schema = self.dataset_metadata.sessions_metadata[0].subject.model_json_schema()
        participants_json = {
            field: info["description"]
            for field, info in participants_schema["properties"].items()
            if is_field_in_table.get(field, False) is True
        }
        participants_json_file_path = bids_directory / "participants.json"
        with participants_json_file_path.open(mode="w") as file_stream:
            json.dump(obj=participants_json, fp=file_stream, indent=4)

        for subject_id in participants_data_frame["participant_id"]:
            subject_directory = bids_directory / f"sub-{subject_id}"
            subject_directory.mkdir(exist_ok=True)
