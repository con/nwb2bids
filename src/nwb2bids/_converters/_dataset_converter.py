import collections
import json
import pathlib
import typing

import pandas
import pydantic
import typing_extensions

from nwb2bids.bids_models import DatasetDescription

from ._session_converter import SessionConverter


class DatasetConverter(pydantic.BaseModel):
    session_converters: list[SessionConverter] = pydantic.Field(
        description="List of session converters. Typically instantiated by calling `.from_nwb_directory()`.",
        min_length=1,
    )
    dataset_description: DatasetDescription | None = pydantic.Field(
        description="The BIDS-compatible dataset description.",
        default=None,
    )

    @classmethod
    @pydantic.validate_call
    def from_nwb_directory(
        cls, nwb_directory: pydantic.DirectoryPath, additional_metadata_file_path: pydantic.FilePath | None = None
    ) -> typing_extensions.Self:
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

        dataset_description = None
        additional_metadata_file_path = (
            secondary_path
            if additional_metadata_file_path is None
            and (secondary_path := nwb_directory / "additional_metadata.json").exists()
            else additional_metadata_file_path
        )
        if additional_metadata_file_path is not None:
            dataset_description = DatasetDescription.from_file_path(file_path=additional_metadata_file_path)

        dataset_converter = cls(session_converters=session_converters, dataset_description=dataset_description)
        return dataset_converter

    def extract_dataset_metadata(self) -> None:
        """
        Deploy the call to `.extract_session_metadata()` for each session converter.
        """
        collections.deque(
            (
                session_converter.extract_session_metadata()
                for session_converter in self.session_converters
                if session_converter.session_metadata is None
            ),
            maxlen=0,
        )

    @pydantic.validate_call
    def convert_to_bids_dataset(
        self, bids_directory: str | pathlib.Path, file_mode: typing.Literal["move", "copy", "symlink"] | None = None
    ) -> None:
        """
        Convert the directory of NWB files to a BIDS dataset.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        file_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
        """
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        if self.dataset_description is not None:
            self.write_dataset_description(bids_directory=bids_directory)

        self.write_participants_metadata(bids_directory=bids_directory)
        self.write_sessions_metadata(bids_directory=bids_directory)

        collections.deque(
            (
                session_converter.convert_to_bids_session(bids_directory=bids_directory, file_mode=file_mode)
                for session_converter in self.session_converters
            ),
            maxlen=0,
        )

    @pydantic.validate_call
    def write_dataset_description(self, bids_directory: str | pathlib.Path) -> None:
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        dataset_description_dictionary = self.dataset_description.model_dump()

        dataset_description_file_path = bids_directory / "dataset_description.json"
        with dataset_description_file_path.open(mode="w") as file_stream:
            json.dump(obj=dataset_description_dictionary, fp=file_stream, indent=4)

    @pydantic.validate_call
    def write_participants_metadata(self, bids_directory: str | pathlib.Path) -> None:
        """
        Write the `participants.tsv` and `participants.json` files.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        participants_data_frame = pandas.DataFrame.from_records(
            data=[
                {
                    key: value
                    for key, value in session_converter.session_metadata.participant.model_dump().items()
                    if value is not None
                }
                for session_converter in self.session_converters
            ]
        ).astype("string")

        # BIDS requires sub- prefix in table values
        participants_data_frame["participant_id"] = participants_data_frame["participant_id"].apply(
            lambda participant_id: f"sub-{participant_id}"
        )
        is_field_in_table = {field: True for field in participants_data_frame.keys()}

        # BIDS Validator is strict regarding column order
        required_column_order = [
            field
            for field in ["participant_id", "species", "sex", "strain"]
            if is_field_in_table.get(field, False) is True
        ]
        column_order = required_column_order + [
            field
            for field in participants_data_frame.columns
            if is_field_in_table.get(field, False) is True and field not in required_column_order
        ]

        participants_tsv_file_path = bids_directory / "participants.tsv"
        participants_data_frame.to_csv(
            path_or_buf=participants_tsv_file_path, mode="w", index=False, sep="\t", columns=column_order
        )

        is_field_in_table = {field: True for field in participants_data_frame.keys()}
        participants_schema = self.session_converters[0].session_metadata.participant.model_json_schema()
        participants_json = {
            field: info["description"]
            for field, info in participants_schema["properties"].items()
            if is_field_in_table.get(field, False) is True
        }
        participants_json_file_path = bids_directory / "participants.json"
        with participants_json_file_path.open(mode="w") as file_stream:
            json.dump(obj=participants_json, fp=file_stream, indent=4)

    @pydantic.validate_call
    def write_sessions_metadata(self, bids_directory: str | pathlib.Path) -> None:
        """
        Write the `_sessions.tsv` and `_sessions.json` files, then create empty participant and session directories.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        subject_id_to_sessions = collections.defaultdict(list)
        for session_converter in self.session_converters:
            subject_id_to_sessions[session_converter.session_metadata.participant.participant_id].append(
                session_converter
            )

        # TODO: expand beyond just session_id field (mainly via additional metadata)
        sessions_schema = self.session_converters[0].session_metadata.model_json_schema()
        sessions_json = {"session_id": sessions_schema["properties"]["session_id"]["description"]}

        for subject_id, sessions_metadata in subject_id_to_sessions.items():
            subject_directory = bids_directory / f"sub-{subject_id}"
            subject_directory.mkdir(exist_ok=True)

            # BIDS requires ses- prefix in table values
            sessions_data_frame = pandas.DataFrame(
                {"session_id": [f"ses-{session_metadata.session_id}" for session_metadata in sessions_metadata]}
            )

            session_tsv_file_path = subject_directory / f"sub-{subject_id}_sessions.tsv"
            sessions_data_frame.to_csv(path_or_buf=session_tsv_file_path, mode="w", index=False, sep="\t")

            session_json_file_path = subject_directory / f"sub-{subject_id}_sessions.json"
            with session_json_file_path.open(mode="w") as file_stream:
                json.dump(obj=sessions_json, fp=file_stream, indent=4)

            for session_metadata in sessions_metadata:
                session_directory = subject_directory / f"ses-{session_metadata.session_id}"
                session_directory.mkdir(exist_ok=True)

    def _establish_bids_directory_and_check_metadata(self, bids_directory: pathlib.Path) -> None:
        bids_directory.mkdir(exist_ok=True)
        if any(session_converter.session_metadata is None for session_converter in self.session_converters):
            self.extract_dataset_metadata()
