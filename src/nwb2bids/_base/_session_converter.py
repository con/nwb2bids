import pathlib
import typing

import pydantic

from ._utils import _get_session_id_from_nwbfile_path
from ..models import BidsSessionMetadata


class SessionConverter(pydantic.BaseModel):
    """
    Initialize a converter of NWB files to BIDS format.

    Parameters
    ----------
    nwbfile_paths : list of file paths
        The list of paths to NWB files associated with this session.
    """

    session_id: str
    nwbfile_paths: list[pydantic.FilePath]
    session_metadata: BidsSessionMetadata | None = None

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
            nwb_file_path: _get_session_id_from_nwbfile_path(nwbfile_path=nwb_file_path)
            for nwb_file_path in nwb_file_paths
        }

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
        bids_directory = pathlib.Path(bids_directory)
        bids_directory.mkdir(exist_ok=True)

        if self.session_metadata is None:
            self.extract_session_metadata()

        session_subdirectory = bids_directory / "TODO"
        session_subdirectory.mkdir(exist_ok=True)

        if copy_mode == "copy":
            pass
        elif copy_mode == "move":
            pass
        elif copy_mode == "symlink":
            pass
