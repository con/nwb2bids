import pathlib
import shutil
import typing

import pydantic
import pynwb
import typing_extensions

from nwb2bids._converters._handle_file_mode import _handle_file_mode
from nwb2bids.bids_models import BidsSessionMetadata


class SessionConverter(pydantic.BaseModel):
    """
    Initialize a converter of NWB files to BIDS format.

    Parameters
    ----------
    nwbfile_paths : list of file paths
        The list of paths to NWB files associated with this session.
    """

    session_id: str = pydantic.Field(
        description="A unique session identifier.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    nwbfile_paths: list[pydantic.FilePath] = pydantic.Field(
        description="List of NWB file paths which share this session ID.", min_length=1
    )
    session_metadata: BidsSessionMetadata | None = pydantic.Field(
        description="BIDS metadata extracted for this session.", default=None
    )

    @classmethod
    @pydantic.validate_call
    def from_nwb_directory(cls, nwb_directory: pydantic.DirectoryPath) -> list[typing_extensions.Self]:
        """
        Initialize a list of session converters from a list of NWB file paths.

        Automatically associates multiple NWB files to a single session according to session ID.

        Parameters
        ----------
        nwb_directory : directory path
            The path to the directory containing NWB files.

        Returns
        -------
        A list of SessionConverter instances, one per unique session ID.
        """
        nwb_file_paths = list(nwb_directory.rglob(pattern="*.nwb"))
        nwb_file_path_to_session_id = {
            nwb_file_path: pynwb.read_nwb(nwb_file_path).session_id for nwb_file_path in nwb_file_paths
        }  # IDEA: if this is too slow, could do direct h5py read instead, to avoid reading the entire file metadata

        unique_session_ids = set(nwb_file_path_to_session_id.values())
        unique_session_id_to_nwb_file_paths = {
            unique_session_id: [
                nwb_file_path
                for nwb_file_path, session_id in nwb_file_path_to_session_id.items()
                if session_id == unique_session_id
            ]
            for unique_session_id in unique_session_ids
        }

        session_converters = [
            cls(session_id=session_id, nwbfile_paths=nwb_file_paths)
            for session_id, nwb_file_paths in unique_session_id_to_nwb_file_paths.items()
        ]
        return session_converters

    def extract_session_metadata(self) -> None:
        """
        Extract metadata from the NWB file across the specified directory.
        """
        self.session_metadata = BidsSessionMetadata.from_nwbfile_paths(nwbfile_paths=self.nwbfile_paths)

    @pydantic.validate_call
    def convert_to_bids_session(
        self, bids_directory: str | pathlib.Path, file_mode: typing.Literal["move", "copy", "symlink"] | None = None
    ) -> None:
        """
        Convert the NWB file to a BIDS session directory.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        file_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
              - "move": Move the files to the BIDS directory.
              - "copy": Copy the files to the BIDS directory.
              - "symlink": Create symbolic links to the files in the BIDS directory.
            The default behavior is to attempt to use symlinks, but fall back to copying if symlinks are not supported.
        """
        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        file_mode = _handle_file_mode(file_mode=file_mode)

        if self.session_metadata is None:
            self.extract_session_metadata()

        subject_id = self.session_metadata.participant.participant_id
        session_subdirectory = bids_directory / f"sub-{subject_id}" / f"ses-{self.session_id}" / "ecephys"
        session_subdirectory.mkdir(parents=True, exist_ok=True)

        self.write_ecephys_files(bids_directory=bids_directory)
        if self.session_metadata.events is not None:
            self.write_events_files(bids_directory=bids_directory)

        # TODO: determine icephys or ecephys suffix
        for nwbfile_path in self.nwbfile_paths:
            session_file_path = session_subdirectory / f"sub-{subject_id}_ses-{self.session_id}_ecephys.nwb"
            if file_mode == "copy":
                shutil.copy(src=nwbfile_path, dst=session_file_path)
            elif file_mode == "move":
                shutil.move(src=nwbfile_path, dst=session_file_path)
            elif file_mode == "symlink":
                session_file_path.symlink_to(target=nwbfile_path)

    @pydantic.validate_call
    def write_ecephys_files(self, bids_directory: str | pathlib.Path) -> None:
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

        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

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
    def write_events_files(self, bids_directory: str | pathlib.Path) -> None:
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
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        ecephys_directory = self._establish_ecephys_subdirectory(bids_directory=bids_directory)
        file_prefix = f"sub-{self.session_metadata.participant.participant_id}_ses-{self.session_id}"
        session_events_tsv_file_path = ecephys_directory / f"{file_prefix}_events.tsv"
        self.session_metadata.events.to_tsv(file_path=session_events_tsv_file_path)

        # TODO: add merging from top-level additional metadata mechanism
        session_events_metadata_file_path = ecephys_directory / f"{file_prefix}_events.json"
        self.session_metadata.events.to_json(file_path=session_events_metadata_file_path)

        # IDEA: check events.json files, see if all are the same and if so remove the duplicates and move to outer level

    def _establish_bids_directory_and_check_metadata(self, bids_directory: pathlib.Path) -> None:
        bids_directory.mkdir(exist_ok=True)
        if self.session_metadata is None:
            self.extract_session_metadata()

    def _establish_ecephys_subdirectory(self, bids_directory: pathlib.Path) -> pathlib.Path:
        subject_directory = bids_directory / f"sub-{self.session_metadata.participant.participant_id}"
        subject_directory.mkdir(exist_ok=True)
        session_directory = subject_directory / f"ses-{self.session_id}"
        session_directory.mkdir(exist_ok=True)
        ecephys_directory = session_directory / "ecephys"
        ecephys_directory.mkdir(exist_ok=True)

        return ecephys_directory
