import typing

from ._base_converter import BaseConverter
from ..schemas import BidsSessionMetadata


class SessionConverter(BaseConverter):
    def extract_metadata(self) -> BidsSessionMetadata:
        # nwb_files = list(self.nwb_directory.rglob(pattern="*.nwb"))
        # all_metadata = dict()
        # for nwb_file in nwb_files:
        #     all_metadata[nwb_file] = _extract_metadata(nwb_file)
        # return all_metadata
        pass

    def convert_to_bids(self, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink") -> None:
        pass
