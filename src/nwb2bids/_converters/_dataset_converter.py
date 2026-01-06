import collections
import json
import traceback

import pandas
import pydantic
import typing_extensions

from ._dandi_utils import get_bids_dataset_description
from ._run_config import RunConfig
from ._session_converter import SessionConverter
from .._converters._base_converter import BaseConverter
from .._inspection._inspection_result import Category, InspectionResult, Severity
from ..bids_models import BidsSessionMetadata, DatasetDescription


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
    def notifications(self) -> list[InspectionResult]:
        """
        All notifications from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        notifications = [
            notification
            for session_converter in self.session_converters
            for notification in session_converter.notifications
        ] + self._internal_notifications
        notifications.sort(
            key=lambda notification: (-notification.category.value, -notification.severity.value, notification.title)
        )
        return notifications

    @classmethod
    @pydantic.validate_call
    def from_remote_dandiset(
        cls,
        dandiset_id: str = pydantic.Field(pattern=r"^\d{6}$"),
        api_url: str | None = None,
        token: str | None = None,
        limit: int | None = None,
        run_config: RunConfig = pydantic.Field(default_factory=lambda: RunConfig()),
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
        run_config : RunConfig, optional
            The configuration for this conversion run.
        """
        try:
            import dandi.dandiapi

            client = dandi.dandiapi.DandiAPIClient(api_url=api_url, token=token)
            version_id = "draft"  # Only allow running on draft version
            dandiset = client.get_dandiset(dandiset_id=dandiset_id, version_id=version_id)

            dataset_description, _internal_notifications = get_bids_dataset_description(dandiset=dandiset)

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
                    run_config=run_config,
                )
                for session_id, assets in sorted_session_id_to_assets.items()
            ]

            dataset_converter = cls(
                session_converters=session_converters, dataset_description=dataset_description, run_config=run_config
            )
            dataset_converter._internal_notifications = _internal_notifications
            return dataset_converter
        except Exception:  # noqa
            _internal_notifications = [
                InspectionResult(
                    title="Failed to initialize converter on remote Dandiset",
                    reason=(
                        "An error occurred while executing `DatasetConverter.from_remote_dandiset`."
                        f"\n\n{traceback.format_exc()}"
                    ),
                    solution="Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
                    category=Category.INTERNAL_ERROR,
                    severity=Severity.ERROR,
                )
            ]

            dataset_converter = cls(session_converters=[], dataset_description=None, run_config=run_config)

        dataset_converter._internal_notifications = _internal_notifications
        return dataset_converter

    @classmethod
    @pydantic.validate_call
    def from_nwb_paths(
        cls,
        nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
        run_config: RunConfig = pydantic.Field(default_factory=lambda: RunConfig()),
    ) -> typing_extensions.Self:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_paths : iterable of file and directory paths
            An iterable of NWB file paths and directories containing NWB files.
        run_config : RunConfig, optional
            The configuration for this conversion run.

        Returns
        -------
        An instance of DatasetConverter.
        """
        try:
            session_converters = SessionConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)

            dataset_description = None
            additional_metadata_file_path = run_config.additional_metadata_file_path
            if additional_metadata_file_path is not None:
                dataset_description = DatasetDescription.from_file_path(file_path=additional_metadata_file_path)

            session_messages = [
                notification
                for session_converter in session_converters
                for notification in session_converter.notifications
            ]

            dataset_converter = cls(
                session_converters=session_converters, dataset_description=dataset_description, run_config=run_config
            )
            dataset_converter._internal_notifications = session_messages
            return dataset_converter
        except Exception:  # noqa
            _internal_notifications = [
                InspectionResult(
                    title="Failed to initialize converter on local NWB files",
                    reason=(
                        "An error occurred while executing `DatasetConverter.from_nwb_paths`."
                        f"\n\n{traceback.format_exc()}"
                    ),
                    solution="Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
                    category=Category.INTERNAL_ERROR,
                    severity=Severity.ERROR,
                )
            ]
            dataset_converter = cls(session_converters=[], dataset_description=None, run_config=run_config)
            dataset_converter._internal_notifications = _internal_notifications
            return dataset_converter

    def extract_metadata(self) -> None:
        try:
            collections.deque(
                (
                    session_converter.extract_metadata()
                    for session_converter in self.session_converters
                    if session_converter.session_metadata is None
                ),
                maxlen=0,
            )
        except Exception:  # noqa
            notification = InspectionResult(
                title="Failed to extract metadata for one or more sessions",
                reason=(
                    "An error occurred while executing `DatasetConverter.extract_metadata`."
                    f"\n\n{traceback.format_exc()}"
                ),
                solution="Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
                category=Category.INTERNAL_ERROR,
                severity=Severity.ERROR,
            )
            self._internal_notifications.append(notification)

    def convert_to_bids_dataset(self) -> None:
        """Convert the directory of NWB files to a BIDS dataset."""
        try:
            for session_converter in self.session_converters:
                session_converter.convert_to_bids_session()

            self.write_participants_metadata()
            self.write_sessions_metadata()
            self.write_dataset_description()
        except Exception:  # noqa
            notification = InspectionResult(
                title="Failed to convert to BIDS dataset",
                reason=(
                    "An error occurred while executing `DatasetConverter.convert_to_bids_dataset`."
                    f"\n\n{traceback.format_exc()}"
                ),
                solution="Please raise an issue on `nwb2bids`: https://github.com/con/nwb2bids/issues.",
                category=Category.INTERNAL_ERROR,
                severity=Severity.ERROR,
            )
            self._internal_notifications.append(notification)
        finally:
            self.run_config.bids_directory.mkdir(exist_ok=True)  # Just in case it failed to create earlier
            self.run_config._nwb2bids_directory.mkdir(exist_ok=True)
            notifications_dump = [notification.model_dump(mode="json") for notification in self.notifications]
            self.run_config.notifications_json_file_path.write_text(data=json.dumps(obj=notifications_dump, indent=2))

    def write_dataset_description(self) -> None:
        """Write the `dataset_description.json` file."""
        if self.dataset_description is None:
            self.dataset_description = DatasetDescription(BIDSVersion="1.10.1", HEDVersion="8.3.0")

        dataset_description_dictionary = self.dataset_description.model_dump()

        dataset_description_file_path = self.run_config.bids_directory / "dataset_description.json"
        with dataset_description_file_path.open(mode="w") as file_stream:
            json.dump(obj=dataset_description_dictionary, fp=file_stream, indent=4)

    def write_participants_metadata(self) -> None:
        """Write the `participants.tsv` and `participants.json` files."""
        model_dump_per_session = []
        for session_converter in self.session_converters:
            model_dump = session_converter.session_metadata.participant.model_dump()
            model_dump_per_session.append(model_dump)

        full_participants_data_frame = pandas.DataFrame.from_records(
            data=[
                {key: value for key, value in model_dump.items() if value is not None}
                for model_dump in model_dump_per_session
            ]
        ).astype("string")

        if full_participants_data_frame.empty:
            return

        # Aggregate values across entries (such as species mismatches)
        cols_to_agg = [col for col in full_participants_data_frame.columns if col != "participant_id"]
        if any(cols_to_agg):
            aggregated_cols = {col: lambda val: ", ".join(val.dropna().unique()) for col in cols_to_agg}
            aggregated_data_frame = full_participants_data_frame.groupby(by="participant_id", as_index=False).agg(
                func=aggregated_cols
            )
        else:
            aggregated_data_frame = full_participants_data_frame.copy()

        # Deduplicate all rows of the frame
        deduplicated_data_frame = aggregated_data_frame.drop_duplicates(ignore_index=True).copy()

        # Apply sanitization
        sanitizations = [converter.session_metadata.sanitization for converter in self.session_converters]
        sanitized_participant_ids = {
            sanitization.original_participant_id: sanitization.sanitized_participant_id
            for sanitization in sanitizations
        }

        with pandas.option_context("mode.chained_assignment", None):
            deduplicated_data_frame["participant_id"] = (
                deduplicated_data_frame["participant_id"]
                .apply(lambda participant_id: sanitized_participant_ids[participant_id])
                .astype("string")
            )

        # BIDS requires sub- prefix in table values
        participants_data_frame = deduplicated_data_frame.copy(deep=True)
        participants_data_frame["participant_id"] = (
            participants_data_frame["participant_id"]
            .apply(lambda participant_id: f"sub-{participant_id}")
            .astype("string")
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

        participants_tsv_file_path = self.run_config.bids_directory / "participants.tsv"
        participants_data_frame.to_csv(
            path_or_buf=participants_tsv_file_path, mode="w", index=False, sep="\t", columns=column_order
        )

        if len(self.session_converters) > 0:
            is_field_in_table = {field: True for field in participants_data_frame.keys()}
            participants_schema = self.session_converters[0].session_metadata.participant.model_json_schema()
            participants_json = {
                field: info["description"]
                for field, info in participants_schema["properties"].items()
                if is_field_in_table.get(field, False) is True
            }
            participants_json_file_path = self.run_config.bids_directory / "participants.json"
            with participants_json_file_path.open(mode="w") as file_stream:
                json.dump(obj=participants_json, fp=file_stream, indent=4)

    def write_sessions_metadata(self) -> None:
        """
        Write the `_sessions.tsv` and `_sessions.json` files, then create empty participant and session directories.
        """
        participant_id_to_sessions = collections.defaultdict(list)
        for session_converter in self.session_converters:
            participant_id_to_sessions[session_converter.session_metadata.sanitization.sanitized_participant_id].append(
                session_converter.session_metadata
            )

        # TODO: expand beyond just session_id field (mainly via additional metadata)
        sessions_schema = BidsSessionMetadata.model_json_schema()
        sessions_json = {"session_id": sessions_schema["properties"]["session_id"]["description"]}

        for participant_id, sessions_metadata in participant_id_to_sessions.items():
            sanitized_participant_id = participant_id
            sanitized_session_ids = [
                session_metadata.sanitization.sanitized_session_id for session_metadata in sessions_metadata
            ]

            subject_directory = self.run_config.bids_directory / f"sub-{sanitized_participant_id}"
            subject_directory.mkdir(exist_ok=True)

            # BIDS requires ses- prefix in table values
            sessions_data_frame = pandas.DataFrame(
                {"session_id": [f"ses-{session_id}" for session_id in sanitized_session_ids]}
            )

            session_tsv_file_path = subject_directory / f"sub-{sanitized_participant_id}_sessions.tsv"
            sessions_data_frame.to_csv(path_or_buf=session_tsv_file_path, mode="w", index=False, sep="\t")

            session_json_file_path = subject_directory / f"sub-{sanitized_participant_id}_sessions.json"
            with session_json_file_path.open(mode="w") as file_stream:
                json.dump(obj=sessions_json, fp=file_stream, indent=4)

            for session_id in sanitized_session_ids:
                session_directory = subject_directory / f"ses-{session_id}"
                session_directory.mkdir(exist_ok=True)
