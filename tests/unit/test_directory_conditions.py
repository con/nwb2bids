import json
import os
import pathlib

import pytest

import nwb2bids


@pytest.mark.parametrize(
    "test_case",
    [
        "explicit_empty",
        "explicit_exists_valid_bids",
        "implicit_empty",
        "implicit_exists_valid_bids",
    ],
)
def test_allowed_directory_conditions(
    test_case: str,
    minimal_nwbfile_path: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    """
    Test the `_handle_bids_directory` conditions on a minimal case of writing the dataset description file.

    The valid conditions for the BIDS directory are:
        1. Explicitly passed and allowed to be empty.
        2. Explicitly passed and already exists as a valid BIDS dataset.
        3. Implicitly the current working directory, which is empty.
        4. Implicitly the current working directory, which is a valid BIDS dataset.
    """
    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"

    if "valid" in test_case:
        dataset_description_file_path.write_text(data='{"BIDSVersion": "1.10"}')

    if "implicit" in test_case:
        initial_working_directory = pathlib.Path.cwd()
        os.chdir(temporary_bids_directory)
        bids_directory = None
    else:
        bids_directory = temporary_bids_directory

    try:
        dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(
            nwb_directory=minimal_nwbfile_path.parent, additional_metadata_file_path=additional_metadata_file_path
        )
        dataset_converter.extract_metadata()

        dataset_converter.write_dataset_description(bids_directory=bids_directory)
    finally:
        if "implicit" in test_case:
            os.chdir(initial_working_directory)

    expected_structure = {temporary_bids_directory: {"directories": set(), "files": {"dataset_description.json"}}}
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"
    with dataset_description_file_path.open(mode="r") as file_stream:
        dataset_description_json = json.load(fp=file_stream)

    expected_dataset_description = {
        "Name": "test",
        "Description": "TODO",
        "BIDSVersion": "1.10",
        "DatasetType": "raw",
        "License": "CC-BY-4.0",
        "Authors": ["Cody Baker", "Yaroslav Halchenko"],
    }
    assert dataset_description_json == expected_dataset_description


@pytest.mark.parametrize(
    "test_case",
    [
        "explicit_no_dataset_description",
        "explicit_no_bids_version",
        "implicit_no_dataset_description",
        "implicit_no_bids_version",
    ],
)
def test_disallowed_directory_conditions(
    test_case: str,
    minimal_nwbfile_path: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"

    if "implicit" in test_case:
        initial_working_directory = pathlib.Path.cwd()
        os.chdir(temporary_bids_directory)
        bids_directory = None
    else:
        bids_directory = temporary_bids_directory

    if "no_dataset_description" in test_case:
        other_file_path = dataset_description_file_path.parent / "other_file.txt"
        other_file_path.write_text(data="This is not a BIDS dataset.")

        expected_exception = "missing 'dataset_description.json'"
    elif "no_bids_version" in test_case:
        dataset_description_file_path.write_text(data='{"Name": "test"}')

        expected_exception = "missing 'BIDSVersion' in 'dataset_description.json'"

    try:
        with pytest.raises(expected_exception=ValueError, match=expected_exception):
            dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(
                nwb_directory=minimal_nwbfile_path.parent, additional_metadata_file_path=additional_metadata_file_path
            )
            dataset_converter.extract_metadata()

            dataset_converter.write_dataset_description(bids_directory=bids_directory)
    finally:
        if "implicit" in test_case:
            os.chdir(initial_working_directory)
