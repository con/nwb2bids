"""Configuration file for the doctests."""
import json
import pathlib
import typing

import pytest


# Doctest directories
@pytest.fixture(autouse=True)
def add_data_space(doctest_namespace: dict[str, typing.Any], tmp_path: pathlib.Path):
    doctest_namespace["path_to_some_directory"] = pathlib.Path(tmp_path)

    tutorial_directory = pathlib.Path.home() / ".nwb2bids/tutorials/ephys_tutorial_file"
    additional_metadata_file_path = tutorial_directory / "metadata.json"

    additional_metadata = {
        "dataset_description": {
            "Name": "My Custom BIDS Dataset",
            "BIDSVersion": "1.8.0",
            "Authors": ["First Last", "Second Author"]
        }
    }
    additional_metadata_file_path.write_text(data=json.dumps(obj=additional_metadata))
