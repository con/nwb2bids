import typing

from ._additional_metadata import _write_dataset_description
from ._base_converter import BaseConverter
from ..schemas import BidsDatasetMetadata


class DatasetConverter(BaseConverter):

    def extract_metadata(self) -> BidsDatasetMetadata:
        # nwb_files = list(self.nwb_directory.rglob(pattern="*.nwb"))
        # all_metadata = dict()
        # for nwb_file in nwb_files:
        #     all_metadata[nwb_file] = _extract_metadata(nwb_file)
        # return all_metadata
        pass

    def convert_to_bids(self, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink") -> None:
        if self.additional_metadata is not None:
            _write_dataset_description(additional_metadata=self.additional_metadata, bids_directory=self.bids_directory)
