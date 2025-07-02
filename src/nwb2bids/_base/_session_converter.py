import json
import pathlib
import shutil
import typing

import pydantic
import pynwb

from ._events_utils import _get_events_metadata, _get_events_table
from ..models import BidsSessionMetadata


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
    def from_nwb_directory(cls, nwb_directory: pydantic.DirectoryPath) -> list[typing.Self]:
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
        self, bids_directory: str | pathlib.Path, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink"
    ) -> None:
        """
        Convert the NWB file to a BIDS session directory.

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
        if self.session_metadata is None:
            self.extract_session_metadata()

        subject_id = self.session_metadata.participant_id
        session_subdirectory = bids_directory / f"sub-{subject_id}" / f"ses-{self.session_id}" / "ephys"
        session_subdirectory.mkdir(parents=True, exist_ok=True)

        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        # TODO: determine icephys or ecephys suffix
        for nwbfile_path in self.nwbfile_paths:
            session_file_path = session_subdirectory / f"sub-{subject_id}_ses-{self.session_id}_ecephys.nwb"
            if copy_mode == "copy":
                shutil.copy(src=nwbfile_path, dst=session_file_path)
            elif copy_mode == "move":
                shutil.move(src=nwbfile_path, dst=session_file_path)
            elif copy_mode == "symlink":
                session_file_path.symlink_to(target=nwbfile_path)

    @pydantic.validate_call
    def write_ecephys_metadata(self, bids_directory: str | pathlib.Path) -> None:
        """
        Write the `_probes`, `_channels`, and `_electrodes` metadata files, both `.tsv` and `.json`, for this session .

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        # for var in ("electrodes", "probes", "channels"):
        #     var_metadata = metadata[var]
        #     # var_metadata = drop_false_keys(var_metadata)
        #     var_metadata_file_path = os.path.join(
        #         bids_directory,
        #         participant_id,
        #         session_id,
        #         "ephys",
        #         f"{file_prefix}_{var}.tsv",
        #     )
        # _write_tsv(var_metadata, var_metadata_file_path)

    @pydantic.validate_call
    def write_events_metadata(self, bids_directory: str | pathlib.Path) -> None:
        """
        Write the `_events.tsv` and `_events.json` files for this session.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        self._establish_bids_directory_and_check_metadata(bids_directory=bids_directory)

        if len(self.nwbfile_paths) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        nwbfile_path = self.nwbfile_paths[0]
        nwbfile = pynwb.read_nwb(nwbfile_path)
        nwb_events_table = _get_events_table(nwbfile=nwbfile)

        if nwb_events_table is None:
            return

        # Collapse 'start_time' and 'stop_time' columns into 'onset' and 'duration' columns
        bids_event_table = nwb_events_table.copy()
        bids_event_table["duration"] = bids_event_table["stop_time"] - bids_event_table["start_time"]
        bids_event_table = bids_event_table.rename(columns={"start_time": "onset"})
        bids_event_table = bids_event_table.drop(columns=["stop_time"])
        bids_event_table = bids_event_table.sort_values(by=["onset", "duration"], ascending=[True, False]).reset_index(
            drop=True
        )

        # BIDS Validator is strict regarding column order
        required_column_order = ["onset", "duration", "nwb_table"]
        column_order = required_column_order + [
            column for column in bids_event_table.columns if column not in required_column_order
        ]

        subject_directory = bids_directory / f"sub-{self.session_metadata.subject.participant_id}"
        subject_directory.mkdir(exist_ok=True)
        session_directory = subject_directory / f"ses-{self.session_id}"
        session_directory.mkdir(exist_ok=True)
        ecephys_directory = session_directory / "ecephys"
        ecephys_directory.mkdir(exist_ok=True)

        file_prefix = f"sub-{self.session_metadata.subject.participant_id}_ses-{self.session_id}"
        session_events_table_file_path = ecephys_directory / f"{file_prefix}_events.tsv"
        bids_event_table.to_csv(
            path_or_buf=session_events_table_file_path,
            sep="\t",
            index=False,
            columns=column_order,
        )

        bids_event_metadata = _get_events_metadata(nwbfile=nwbfile)
        additional_events = (
            self.session_metadata.events.events.model_dump()
            if self.session_metadata.events is not None
            else None or dict()
        )
        for key, value in additional_events.items():
            if key not in bids_event_metadata:
                bids_event_metadata[key] = value
            else:
                bids_event_metadata[key].update(value)

        session_events_metadata_file_path = ecephys_directory / f"{file_prefix}_events.json"
        with session_events_metadata_file_path.open(mode="w") as file_stream:
            json.dump(obj=bids_event_metadata, fp=file_stream, indent=4)

        # IDEA: check events.json files, see if all are the same and if so remove the duplicates and move to outer level

    def _establish_bids_directory_and_check_metadata(self, bids_directory: pathlib.Path) -> None:
        bids_directory.mkdir(exist_ok=True)
        if self.session_metadata is None:
            self.extract_session_metadata()
