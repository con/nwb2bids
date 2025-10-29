import json
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
    monkeypatch,
):
    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"

    if "valid" in test_case:
        dataset_description_file_path.write_text(data='{"BIDSVersion": "1.10"}')

    bids_directory = None
    if "implicit" in test_case:
        monkeypatch.chdir(temporary_bids_directory)
    else:
        bids_directory = temporary_bids_directory

    nwb_paths = [minimal_nwbfile_path]
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=nwb_paths, additional_metadata_file_path=additional_metadata_file_path
    )
    dataset_converter.extract_metadata()
    dataset_converter.write_dataset_description(bids_directory=bids_directory)

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
        "GeneratedBy": [
            {
                "Name": "nwb2bids",
                "Version": dataset_description_json["GeneratedBy"][0]["Version"],  # Use actual version from output
                "Description": "Tool to reorganize NWB files into a BIDS directory layout.",
                "CodeURL": "https://github.com/con/nwb2bids",
            }
        ],
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
    monkeypatch,
):
    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"

    bids_directory = None
    if "implicit" in test_case:
        monkeypatch.chdir(temporary_bids_directory)
    else:
        bids_directory = temporary_bids_directory

    if "no_dataset_description" in test_case:
        other_file_path = dataset_description_file_path.parent / "other_file.txt"
        other_file_path.write_text(data="This is not a BIDS dataset.")

        expected_exception = "missing 'dataset_description.json'"
    elif "no_bids_version" in test_case:
        dataset_description_file_path.write_text(data='{"Name": "test"}')

        expected_exception = "missing 'BIDSVersion' in 'dataset_description.json'"

    with pytest.raises(expected_exception=ValueError, match=expected_exception):
        nwb_paths = [minimal_nwbfile_path]
        dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
            nwb_paths=nwb_paths, additional_metadata_file_path=additional_metadata_file_path
        )
        dataset_converter.extract_metadata()
        dataset_converter.write_dataset_description(bids_directory=bids_directory)
