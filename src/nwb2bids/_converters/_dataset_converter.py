import collections
import json
import pathlib
import typing

import pandas
import pydantic
import typing_extensions

from ._dandi_utils import get_bids_dataset_description
from ._session_converter import SessionConverter
from .._converters._base_converter import BaseConverter
from .._inspection._inspection_message import InspectionResult
from ..bids_models import DatasetDescription


class DatasetConverter(BaseConverter):
    session_converters: list[SessionConverter] = pydantic.Field(
        description="List of session converters. Typically instantiated by calling `.from_nwb_paths()`."
    )
    dataset_description: DatasetDescription | None = pydantic.Field(
        description="The BIDS-compatible dataset description.",
        default=None,
    )

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        messages = [message for session_converter in self.session_converters for message in session_converter.messages]
        messages.sort(key=lambda message: (message.category.value, -message.severity.value, message.title))
        return messages

    @classmethod
    @pydantic.validate_call
    def from_remote_dandiset(
        cls,
        dandiset_id: str = pydantic.Field(pattern=r"^\d{6}$"),
        api_url: str | None = None,
        token: str | None = None,
        limit: int | None = None,
    ) -> typing_extensions.Self | None:
        """
        Initialize a converter of a Dandiset to BIDS format.

        Parameters
        ----------
        dandiset_id : str
            The dandiset ID of the Dandiset to be converted.
        api_url : str, optional
            The API URL of a custom DANDI instance to use. If not provided, the API URL of the
            DANDI instance specified by the :envvar:`DANDI_INSTANCE` environment variable
            is used. If the :envvar:`DANDI_INSTANCE` environment variable is not specified,
            The API URL of the `"dandi"` DANDI instance is used.
        token : str, optional
            The authentication token for accessing the DANDI instance.
            If not provided, will attempt to read from the environment variable `DANDI_API_KEY` if it exists.
            This is required for accessing embargoed Dandisets.
        limit : int, optional
            If specified, limits the number of sessions to convert.
            This is mainly useful for testing purposes.
        """
        import dandi.dandiapi

        client = dandi.dandiapi.DandiAPIClient(api_url=api_url, token=token)
        version_id = "draft"  # Only allow running on draft version
        dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=version_id)

        dataset_description = get_bids_dataset_description(dandiset=dandiset)

        if limit is None:
            assets = list(dandiset.get_assets())
        else:
            assets = [asset for counter, asset in enumerate(dandiset.get_assets()) if counter < limit]

        session_id_to_assets = collections.defaultdict(list)
        for asset in assets:
            asset_metadata = asset.get_raw_metadata()

            for session in asset_metadata.get("wasGeneratedBy", []):
                if session.get("schemaKey", "") != "Session":
                    continue

                session_id = session.get("identifier", "")
                if session_id == "":
                    continue

                session_id_to_assets[session_id].append(asset)
        sorted_session_id_to_assets = dict(sorted(session_id_to_assets.items(), key=lambda item: item[0]))

        session_converters = [
            SessionConverter(
                session_id=session_id,
                nwbfile_paths=[asset.get_content_url(follow_redirects=1, strip_query=True) for asset in assets],
            )
            for session_id, assets in sorted_session_id_to_assets.items()
        ]

        dataset_converter = cls(session_converters=session_converters, dataset_description=dataset_description)
        return dataset_converter

    @classmethod
    @pydantic.validate_call
    def from_nwb_paths(
        cls,
        nwb_paths: typing.Iterable[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
        additional_metadata_file_path: pydantic.FilePath | None = None,
    ) -> typing_extensions.Self:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_paths : iterable of file and directory paths
            An iterable of NWB file paths and directories containing NWB files.
        additional_metadata_file_path : file path, optional
            The path to a JSON file containing additional metadata to be included in the BIDS dataset.

        Returns
        -------
        An instance of DatasetConverter.
        """
        session_converters = SessionConverter.from_nwb_paths(nwb_paths=nwb_paths)

        dataset_description = None
        if additional_metadata_file_path is not None:
            dataset_description = DatasetDescription.from_file_path(file_path=additional_metadata_file_path)

        session_messages = [
            message
            for session_converter in session_converters
            for message in session_converter.messages
            if session_converter.messages is not None
        ]
        messages = session_messages if len(session_messages) > 0 else None

        dataset_converter = cls(
            session_converters=session_converters, dataset_description=dataset_description, messages=messages
        )
        return dataset_converter

    def extract_metadata(self) -> None:
        collections.deque(
            (
                session_converter.extract_metadata()
                for session_converter in self.session_converters
                if session_converter.session_metadata is None
            ),
            maxlen=0,
        )

    @pydantic.validate_call
    def convert_to_bids_dataset(
        self,
        bids_directory: str | pathlib.Path | None = None,
        file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    ) -> None:
        """
        Convert the directory of NWB files to a BIDS dataset.

        Parameters
        ----------
        bids_directory : directory path, optional
            The path to the directory where the BIDS dataset will be created.
            If not specified, the current working directory will be used if it is valid to become a BIDS dataset.
            To be a valid BIDS dataset, the directory must either start off empty or otherwise contain BIDS-compatible
            files, such as `dataset_description.json`, `participants.tsv`, `README.md`, and so on.
        file_mode : one of "move", "copy", "symlink", or "auto", default: "auto"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
            - "auto": Decides between all the above based on the system, with preference for linking when possible.
        """
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)

        if self.dataset_description is not None:
            self.write_dataset_description(bids_directory=bids_directory)

        self.write_participants_metadata(bids_directory=bids_directory)
        self.write_sessions_metadata(bids_directory=bids_directory)

        generator = (
            session_converter.convert_to_bids_session(bids_directory=bids_directory, file_mode=file_mode)
            for session_converter in self.session_converters
        )
        collections.deque(generator, maxlen=0)

    @pydantic.validate_call
    def write_dataset_description(self, bids_directory: str | pathlib.Path | None = None) -> None:
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)

        dataset_description_dictionary = self.dataset_description.model_dump()

        dataset_description_file_path = bids_directory / "dataset_description.json"
        with dataset_description_file_path.open(mode="w") as file_stream:
            json.dump(obj=dataset_description_dictionary, fp=file_stream, indent=4)

    @pydantic.validate_call
    def write_participants_metadata(self, bids_directory: str | pathlib.Path | None = None) -> None:
        """
        Write the `participants.tsv` and `participants.json` files.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)

        model_dump_per_session = []
        for session_converter in self.session_converters:
            model_dump = session_converter.session_metadata.participant.model_dump()
            model_dump_per_session.append(model_dump)

        participants_data_frame = pandas.DataFrame.from_records(
            data=[
                {key: value for key, value in model_dump.items() if value is not None}
                for model_dump in model_dump_per_session
            ]
        ).astype("string")

        if participants_data_frame.empty:
            return

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
    def write_sessions_metadata(self, bids_directory: str | pathlib.Path | None = None) -> None:
        """
        Write the `_sessions.tsv` and `_sessions.json` files, then create empty participant and session directories.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)

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
