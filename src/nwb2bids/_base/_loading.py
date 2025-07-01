import json
import pathlib

from ..schemas import AdditionalMetadata


def _load_and_validate_additional_metadata(*, file_path: pathlib.Path) -> AdditionalMetadata:
    with file_path.open(mode="r") as file_stream:
        additional_metadata_dict = json.load(fp=file_stream)

    additional_metadata = AdditionalMetadata(**additional_metadata_dict)
    return additional_metadata
