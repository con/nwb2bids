import collections
import pathlib
import shutil
import typing

import pydantic
import typing_extensions

from ._base_converter import BaseConverter
from .._tools import cache_read_nwb
from ..bids_models import BidsSessionMetadata


class SessionConverter(BaseConverter):
    """
    Initialize a converter of NWB files to BIDS format.
    """

    session_id: str = pydantic.Field(
        description="A unique session identifier.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    nwbfile_paths: list[pydantic.FilePath] | list[pydantic.HttpUrl] = pydantic.Field(
        description="List of NWB file paths which share this session ID.", min_length=1
    )
    session_metadata: BidsSessionMetadata | None = pydantic.Field(
        description="BIDS metadata extracted for this session.", default=None
    )

    @classmethod
    @pydantic.validate_call
    def from_nwb_paths(
        cls,
        nwb_paths: typing.Iterable[pydantic.FilePath | pydantic.DirectoryPath] = pydantic.Field(min_length=1),
    ) -> list[typing_extensions.Self]:
        """
        Initialize a list of session converters from a list of NWB file paths.

        Automatically associates multiple NWB files to a single session according to session ID.

        Parameters
        ----------
        nwb_paths : iterable of file and directory paths
            An iterable of NWB file paths and directories containing NWB files.

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
            unique_session_id_to_nwbfile_paths[
                # IDEA: if this is too slow, could do direct h5py read instead,
                # to avoid reading the entire file metadata
                cache_read_nwb(nwbfile_path).session_id
            ].append(nwbfile_path)

        session_converters = [
            cls(session_id=session_id, nwbfile_paths=nwbfile_paths)
            for session_id, nwbfile_paths in unique_session_id_to_nwbfile_paths.items()
        ]
        return session_converters

    def extract_metadata(self) -> None:
        if self.session_metadata is None:
            self.session_metadata = BidsSessionMetadata.from_nwbfile_paths(nwbfile_paths=self.nwbfile_paths)

    @pydantic.validate_call
    def convert_to_bids_session(
        self,
        bids_directory: str | pathlib.Path | None = None,
        file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    ) -> None:
        """
        Convert the NWB file to a BIDS session directory.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        file_mode : one of "move", "copy", "symlink", or "auto", default: "auto"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
            - "auto": Decides between all the above based on the system, with preference for linking when possible.
        """
        if len(self.nwbfile_paths) > 1:
            message = (
                "Conversion of multiple NWB files per session is not yet supported. "
                "Please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss the use case."
            )
            raise NotImplementedError(message)
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)
        file_mode = self._handle_file_mode(file_mode=file_mode)

        if self.session_metadata is None:
            self.extract_metadata()

        subject_id = self.session_metadata.participant.participant_id
        session_subdirectory = bids_directory / f"sub-{subject_id}" / f"ses-{self.session_id}" / "ecephys"
        session_subdirectory.mkdir(parents=True, exist_ok=True)

        self.write_ecephys_files(bids_directory=bids_directory)
        if self.session_metadata.events is not None:
            self.write_events_files(bids_directory=bids_directory)

        # TODO: determine icephys or ecephys suffix
        for nwbfile_path in self.nwbfile_paths:
            session_file_path = session_subdirectory / f"sub-{subject_id}_ses-{self.session_id}_ecephys.nwb"

            # If not a local path, then it is a URL, so write simple 'symlink' pointing to the URL
            if not isinstance(nwbfile_path, pathlib.Path):
                with session_file_path.open(mode="w") as file_stream:
                    file_stream.write(str(nwbfile_path))
                continue

            if file_mode == "copy":
                shutil.copy(src=nwbfile_path, dst=session_file_path)
            elif file_mode == "move":
                shutil.move(src=nwbfile_path, dst=session_file_path)
            elif file_mode == "symlink":
                session_file_path.symlink_to(target=nwbfile_path)

    @pydantic.validate_call
    def write_ecephys_files(self, bids_directory: str | pathlib.Path | None = None) -> None:
        """
        Write the `_probes`, `_channels`, and `_electrodes` metadata files, both `.tsv` and `.json`, for this session .

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
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
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)
        ecephys_directory = self._establish_ecephys_subdirectory(bids_directory=bids_directory)

        file_prefix = f"sub-{self.session_metadata.participant.participant_id}_ses-{self.session_id}"

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

    @pydantic.validate_call
    def write_events_files(self, bids_directory: str | pathlib.Path | None = None) -> None:
        """
        Write the `_events.tsv` and `_events.json` files for this session.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        if self.session_metadata.events is None:
            message = "No events metadata found in the session metadata - unable to write events TSV."
            raise ValueError(message)
        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        bids_directory = self._handle_bids_directory(bids_directory=bids_directory)
        ecephys_directory = self._establish_ecephys_subdirectory(bids_directory=bids_directory)

        file_prefix = f"sub-{self.session_metadata.participant.participant_id}_ses-{self.session_id}"
        session_events_tsv_file_path = ecephys_directory / f"{file_prefix}_events.tsv"
        self.session_metadata.events.to_tsv(file_path=session_events_tsv_file_path)

        # TODO: add merging from top-level additional metadata mechanism
        session_events_metadata_file_path = ecephys_directory / f"{file_prefix}_events.json"
        self.session_metadata.events.to_json(file_path=session_events_metadata_file_path)

        # IDEA: check events.json files, see if all are the same and if so remove the duplicates and move to outer level

    def _establish_ecephys_subdirectory(self, bids_directory: pathlib.Path) -> pathlib.Path:
        subject_directory = bids_directory / f"sub-{self.session_metadata.participant.participant_id}"
        subject_directory.mkdir(exist_ok=True)
        session_directory = subject_directory / f"ses-{self.session_id}"
        session_directory.mkdir(exist_ok=True)
        ecephys_directory = session_directory / "ecephys"
        ecephys_directory.mkdir(exist_ok=True)

        return ecephys_directory
