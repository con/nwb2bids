"""Unit tests for the `DatasetConverter` class and its methods."""

import json
import pathlib

import pandas
import pytest

import nwb2bids


def test_dataset_converter_directory_initialization(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path.parent]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)

    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)
    assert isinstance(dataset_converter.session_converters, list)
    assert len(dataset_converter.session_converters) == 1
    assert isinstance(dataset_converter.session_converters[0], nwb2bids.SessionConverter)


def test_dataset_converter_file_paths_initialization(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)

    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)
    assert isinstance(dataset_converter.session_converters, list)
    assert len(dataset_converter.session_converters) == 1
    assert isinstance(dataset_converter.session_converters[0], nwb2bids.SessionConverter)


def test_dataset_converter_both_file_and_directory_initialization(
    minimal_nwbfile_path: pathlib.Path, ecephys_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path.parent, ecephys_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)

    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)
    assert isinstance(dataset_converter.session_converters, list)
    assert len(dataset_converter.session_converters) == 2
    assert all(isinstance(converter, nwb2bids.SessionConverter) for converter in dataset_converter.session_converters)


def test_dataset_converter_metadata_extraction(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()

    expected_session_converters = [
        nwb2bids.SessionConverter(
            run_config=run_config,
            session_id="456",
            nwbfile_paths=[minimal_nwbfile_path],
            session_metadata=nwb2bids.bids_models.BidsSessionMetadata(
                session_id="456",
                participant=nwb2bids.bids_models.Participant(
                    participant_id="123", species="Mus musculus", sex="M", strain=None
                ),
            ),
        ),
    ]
    assert dataset_converter.session_converters == expected_session_converters


def test_dataset_converter_write_dataset_description(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(
        bids_directory=temporary_bids_directory, additional_metadata_file_path=additional_metadata_file_path
    )
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()
    dataset_converter.write_dataset_description()

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


def test_dataset_converter_write_dataset_description_with_user_generated_by(
    minimal_nwbfile_path: pathlib.Path,
    additional_metadata_with_generated_by_file_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(
        bids_directory=temporary_bids_directory,
        additional_metadata_file_path=additional_metadata_with_generated_by_file_path,
    )
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()
    dataset_converter.write_dataset_description()

    dataset_description_file_path = temporary_bids_directory / "dataset_description.json"
    with dataset_description_file_path.open(mode="r") as file_stream:
        dataset_description_json = json.load(fp=file_stream)

    # User's custom pipeline should be first, nwb2bids appended second
    expected_dataset_description = {
        "Name": "test",
        "Description": "Dataset with user-provided GeneratedBy",
        "BIDSVersion": "1.10",
        "DatasetType": "raw",
        "License": "CC-BY-4.0",
        "Authors": ["Cody Baker", "Yaroslav Halchenko"],
        "GeneratedBy": [
            {
                "Name": "custom-pipeline",
                "Version": "1.0.0",
                "Description": "Custom data processing pipeline",
                "CodeURL": "https://github.com/example/custom-pipeline",
            },
            {
                "Name": "nwb2bids",
                "Version": dataset_description_json["GeneratedBy"][1]["Version"],  # Use actual version from output
                "Description": "Tool to reorganize NWB files into a BIDS directory layout.",
                "CodeURL": "https://github.com/con/nwb2bids",
            },
        ],
    }
    assert dataset_description_json == expected_dataset_description


def test_dataset_converter_write_subject_metadata(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()

    dataset_converter.write_participants_metadata()

    expected_structure = {
        temporary_bids_directory: {
            "directories": set(),
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        }
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    participants_tsv_file_path = temporary_bids_directory / "participants.tsv"
    participants_data_frame = pandas.read_csv(filepath_or_buffer=participants_tsv_file_path, sep="\t", dtype=str)

    expected_data_frame = pandas.DataFrame({"participant_id": ["sub-123"], "species": ["Mus musculus"], "sex": ["M"]})
    pandas.testing.assert_frame_equal(left=participants_data_frame, right=expected_data_frame)

    participants_json_file_path = temporary_bids_directory / "participants.json"
    with participants_json_file_path.open(mode="r") as file_stream:
        participants_json = json.load(fp=file_stream)
    expected_participants_json = {
        "participant_id": "A unique identifier for this participant.",
        "species": (
            "The species should be the proper Latin binomial species name from the NCBI Taxonomy "
            "(for example, Mus musculus)."
        ),
        "sex": (
            'String value indicating phenotypical sex, one of "male", "female", "other".\n'
            '\tFor "male", use one of these values: male, m, M, MALE, Male.\n'
            '\tFor "female", use one of these values: female, f, F, FEMALE, Female.\n'
            '\tFor "other", use one of these values: other, o, O, OTHER, Other.'
        ),
    }
    assert participants_json == expected_participants_json


def test_dataset_converter_write_sessions_metadata(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()

    dataset_converter.write_sessions_metadata()

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": {"dataset_description.json"}},
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": set(),
            "files": set(),
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    sessions_tsv_file_path = temporary_bids_directory / "sub-123" / "sub-123_sessions.tsv"
    sessions_data_frame = pandas.read_csv(filepath_or_buffer=sessions_tsv_file_path, sep="\t", dtype=str)

    expected_data_frame = pandas.DataFrame({"session_id": ["ses-456"]})
    pandas.testing.assert_frame_equal(left=sessions_data_frame, right=expected_data_frame)

    sessions_json_file_path = temporary_bids_directory / "sub-123" / "sub-123_sessions.json"
    with sessions_json_file_path.open(mode="r") as file_stream:
        sessions_json = json.load(fp=file_stream)
    expected_sessions_json = {"session_id": "A unique session identifier."}
    assert sessions_json == expected_sessions_json


def test_dataset_description_validates_exactly_one_nwb2bids():
    """Test that DatasetDescription enforces exactly one nwb2bids entry in GeneratedBy."""
    # Should fail if user provides nwb2bids (results in 2 after model_post_init)
    with pytest.raises(ValueError, match="GeneratedBy must contain exactly one nwb2bids entry, found 2"):
        nwb2bids.bids_models.DatasetDescription(
            Name="Test",
            BIDSVersion="1.10",
            GeneratedBy=[
                {
                    "Name": "nwb2bids",
                    "Version": "1.0.0",
                    "Description": "User provided nwb2bids",
                    "CodeURL": "https://example.com",
                }
            ],
        )

    # Should succeed with no GeneratedBy (auto-adds nwb2bids)
    dd = nwb2bids.bids_models.DatasetDescription(
        Name="Test",
        BIDSVersion="1.10",
    )
    assert len(dd.GeneratedBy) == 1
    assert dd.GeneratedBy[0].Name == "nwb2bids"

    # Should succeed with user pipeline (auto-appends nwb2bids)
    dd = nwb2bids.bids_models.DatasetDescription(
        Name="Test",
        BIDSVersion="1.10",
        GeneratedBy=[
            {
                "Name": "custom-pipeline",
                "Version": "2.0.0",
                "Description": "Custom",
                "CodeURL": "https://example.com",
            }
        ],
    )
    assert len(dd.GeneratedBy) == 2
    assert dd.GeneratedBy[0].Name == "custom-pipeline"
    assert dd.GeneratedBy[1].Name == "nwb2bids"
