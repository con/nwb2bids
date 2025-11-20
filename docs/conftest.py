"""Configuration file for the doctests."""
import json
import pathlib
import typing

import pytest

import nwb2bids


# Doctest directories
@pytest.fixture(autouse=True)
def add_data_space(doctest_namespace: dict[str, typing.Any], tmp_path: pathlib.Path):
    doctest_namespace["path_to_some_directory"] = pathlib.Path(tmp_path)

    nwb2bids.testing.generate_ephys_tutorial(mode="file")
    nwb2bids.testing.generate_ephys_tutorial(mode="dataset")

    tutorial_directory = nwb2bids.testing.get_tutorial_directory() / "ephys_tutorial_file"
    additional_metadata_file_path = tutorial_directory / "metadata.json"

    additional_metadata = {
        "dataset_description": {
            "Name": "My Custom BIDS Dataset",
            "BIDSVersion": "1.8.0",
            "Authors": ["First Last", "Second Author"]
        }
    }
    additional_metadata_file_path.write_text(data=json.dumps(obj=additional_metadata))
