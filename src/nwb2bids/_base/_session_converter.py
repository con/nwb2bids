import pathlib
import typing

import pydantic

from ..schemas import BidsSessionMetadata


class SessionConverter(pydantic.BaseModel):
    def __init__(
        self,
        nwb_file_path: pydantic.FilePath,
        bids_directory: str | pathlib.Path,
    ) -> None:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_directory : directory path
            The path to the directory containing NWB files.
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        """
        self.nwb_file_path = pathlib.Path(nwb_file_path)
        self.bids_directory = pathlib.Path(bids_directory)

    def extract_session_metadata(self) -> BidsSessionMetadata:
        """
        Extract metadata from the NWB file across the specified directory.
        """
        # nwb_files = list(self.nwb_directory.rglob(pattern="*.nwb"))
        # all_metadata = dict()
        # for nwb_file in nwb_files:
        #     all_metadata[nwb_file] = _extract_metadata(nwb_file)
        # return all_metadata
        pass

    def convert_to_bids_session(self, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink") -> None:
        """
        Convert the NWB file to a BIDS session directory.

        Parameters
        ----------
        copy_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
        """
        pass
