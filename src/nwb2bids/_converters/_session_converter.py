import collections
import pathlib
import shutil

import pydantic
import typing_extensions

from ._run_config import RunConfig
from .._converters._base_converter import BaseConverter
from .._inspection._inspection_result import InspectionResult
from .._tools import cache_read_nwb
from ..bids_models import BidsSessionMetadata


class SessionConverter(BaseConverter):
    """
    Initialize a converter of NWB files to BIDS format.
    """

    session_id: str = pydantic.Field(
        description="A unique session identifier.",
    )
    nwbfile_paths: list[pydantic.FilePath] | list[pydantic.HttpUrl] = pydantic.Field(
        description="List of file paths or URLs of NWB files which share this session ID.", min_length=1
    )
    session_metadata: BidsSessionMetadata | None = pydantic.Field(
        description="BIDS metadata extracted for this session.", default=None
    )
    messages: list[InspectionResult] = pydantic.Field(
        description="List of auto-detected suggestions.", ge=0, default_factory=list
    )

    @classmethod
    @pydantic.validate_call
    def from_nwb_paths(
        cls,
        nwb_paths: list[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
        run_config: RunConfig = pydantic.Field(default_factory=RunConfig),
    ) -> list[typing_extensions.Self]:
        """
        Initialize a list of session converters from a list of NWB file paths.

        Automatically associates multiple NWB files to a single session according to session ID.

        Parameters
        ----------
        nwb_paths : iterable of file and directory paths
            An iterable of NWB file paths and directories containing NWB files.
        run_config : RunConfig, optional
            The configuration for this conversion run.

        Returns
        -------
        A list of SessionConverter instances, one per unique session ID.
        """
        all_nwbfile_paths = []
        for nwb_path in nwb_paths:
            if nwb_path.is_file():
                all_nwbfile_paths.append(nwb_path)
            elif nwb_path.is_dir():
                all_nwbfile_paths += list(nwb_path.rglob(pattern="*.nwb"))

        unique_session_id_to_nwbfile_paths = collections.defaultdict(list)
        for nwbfile_path in all_nwbfile_paths:
            unique_session_id_to_nwbfile_paths[cache_read_nwb(nwbfile_path).session_id].append(nwbfile_path)

        session_converters = [
            cls(
                session_id=session_id or "0",  # Always include `ses-` entity, even for single-session subjects
                nwbfile_paths=nwbfile_paths,
                run_config=run_config,
            )
            for session_id, nwbfile_paths in unique_session_id_to_nwbfile_paths.items()
        ]
        return session_converters

    def extract_metadata(self) -> None:
        if self.session_metadata is None:
            self.session_metadata = BidsSessionMetadata.from_nwbfile_paths(nwbfile_paths=self.nwbfile_paths)
            self.messages += self.session_metadata.messages

    def convert_to_bids_session(self) -> None:
        """
        Convert the NWB file to a BIDS session directory.
        """
        if len(self.nwbfile_paths) > 1:
            message = (
                "Conversion of multiple NWB files per session is not yet supported. "
                "Please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
            )
            raise NotImplementedError(message)

        if self.session_metadata is None:
            self.extract_metadata()

        participant_id = self.session_metadata.participant.participant_id
        session_id = self.session_id
        file_prefix = f"sub-{participant_id}_ses-{session_id}"

        self.write_ecephys_files()
        if self.session_metadata.events is not None:
            self.write_events_files()

        # TODO: determine icephys or ecephys suffix
        ecephys_directory = self._establish_ecephys_subdirectory()
        for nwbfile_path in self.nwbfile_paths:
            session_file_path = ecephys_directory / f"{file_prefix}_ecephys.nwb"

            # If not a local path, then it is a URL, so write simple 'symlink' pointing to the URL
            if not isinstance(nwbfile_path, pathlib.Path):
                with session_file_path.open(mode="w") as file_stream:
                    file_stream.write(str(nwbfile_path))
                continue

            if self.run_config.file_mode == "copy":
                shutil.copy(src=nwbfile_path, dst=session_file_path)
            elif self.run_config.file_mode == "move":
                shutil.move(src=nwbfile_path, dst=session_file_path)
            elif self.run_config.file_mode == "symlink":
                session_file_path.symlink_to(target=nwbfile_path)

    def write_ecephys_files(self) -> None:
        """
        Write the `_probes`, `_channels`, and `_electrodes` metadata files, both `.tsv` and `.json`, for this session .
        """
        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        if (
            self.session_metadata.probe_table is None
            and self.session_metadata.channel_table is None
            and self.session_metadata.electrode_table is None
        ):
            return

        participant_id = self.session_metadata.participant.participant_id
        session_id = self.session_id
        file_prefix = f"sub-{participant_id}_ses-{session_id}"

        ecephys_directory = self._establish_ecephys_subdirectory()
        if self.session_metadata.probe_table is not None:
            probes_tsv_file_path = ecephys_directory / f"{file_prefix}_probes.tsv"
            self.session_metadata.probe_table.to_tsv(file_path=probes_tsv_file_path)

            probes_json_file_path = ecephys_directory / f"{file_prefix}_probes.json"
            self.session_metadata.probe_table.to_json(file_path=probes_json_file_path)

        if self.session_metadata.channel_table is not None:
            channels_tsv_file_path = ecephys_directory / f"{file_prefix}_channels.tsv"
            self.session_metadata.channel_table.to_tsv(file_path=channels_tsv_file_path)

            channels_json_file_path = ecephys_directory / f"{file_prefix}_channels.json"
            self.session_metadata.channel_table.to_json(file_path=channels_json_file_path)

        if self.session_metadata.electrode_table is not None:
            electrodes_tsv_file_path = ecephys_directory / f"{file_prefix}_electrodes.tsv"
            self.session_metadata.electrode_table.to_tsv(file_path=electrodes_tsv_file_path)

            electrodes_json_file_path = ecephys_directory / f"{file_prefix}_electrodes.json"
            self.session_metadata.electrode_table.to_json(file_path=electrodes_json_file_path)

    def write_events_files(self) -> None:
        """Write the `_events.tsv` and `_events.json` files for this session."""
        if self.session_metadata.events is None:
            message = "No events metadata found in the session metadata - unable to write events TSV."
            raise ValueError(message)
        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        participant_id = self.session_metadata.participant.participant_id
        session_id = self.session_id
        file_prefix = f"sub-{participant_id}_ses-{session_id}"

        ecephys_directory = self._establish_ecephys_subdirectory()
        session_events_tsv_file_path = ecephys_directory / f"{file_prefix}_events.tsv"
        self.session_metadata.events.to_tsv(file_path=session_events_tsv_file_path)

        # TODO: add merging from top-level additional metadata mechanism
        session_events_metadata_file_path = ecephys_directory / f"{file_prefix}_events.json"
        self.session_metadata.events.to_json(file_path=session_events_metadata_file_path)

    def _establish_ecephys_subdirectory(self) -> pathlib.Path:
        participant_id = self.session_metadata.participant.participant_id
        session_id = self.session_id

        subject_directory = self.run_config.bids_directory / f"sub-{participant_id}"
        subject_directory.mkdir(exist_ok=True)
        session_directory = subject_directory / f"ses-{session_id}"
        session_directory.mkdir(exist_ok=True)
        ecephys_directory = session_directory / "ecephys"
        ecephys_directory.mkdir(exist_ok=True)

        return ecephys_directory
