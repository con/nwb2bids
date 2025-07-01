import json
import pathlib

from ..schemas import AdditionalMetadata


def _load_and_validate_additional_metadata(*, file_path: pathlib.Path) -> AdditionalMetadata:
    with file_path.open(mode="r") as file_stream:
        additional_metadata_dict = json.load(fp=file_stream)

    additional_metadata = AdditionalMetadata(**additional_metadata_dict)
    return additional_metadata


def _write_dataset_description(*, additional_metadata: AdditionalMetadata, bids_directory: pathlib.Path) -> None:
    content = additional_metadata.dataset_description.model_dump_json(indent=4)

    file_path = bids_directory / "dataset_description.json"
    with open(file=file_path, mode="w") as file_stream:
        file_stream.write(content)
