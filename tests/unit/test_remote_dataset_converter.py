"""Unit tests for the `DatasetConverter` class and its methods."""

import json
import pathlib

import pandas
import pydantic
import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_dataset_converter_initialization(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003")
    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)


@pytest.mark.remote
def test_remote_dataset_converter_metadata_extraction(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003")
    dataset_converter.extract_metadata()

    assert len(dataset_converter.session_converters) == 101

    session_converter = dataset_converter.session_converters[0]
    assert session_converter.session_id == "YutaMouse44-151128"
    assert session_converter.nwbfile_paths == [
        pydantic.HttpUrl("https://dandiarchive.s3.amazonaws.com/blobs/b9c/99c/b9c99cba-0f2b-469c-9747-22c69ac8170f")
    ]

    session_metadata = session_converter.session_metadata
    assert session_metadata.participant == nwb2bids.bids_models.Participant(
        participant_id="YutaMouse44", species="Mus musculus", sex=None, strain=None
    )
    assert session_metadata.events is None
    assert session_metadata.probe_table == nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(
                probe_id="Implant", type=None, description="Silicon electrodes on Intan probe.", manufacturer=None
            )
        ]
    )
    assert session_metadata.channel_table is not None
    assert session_metadata.channel_table[0] == 1
    assert session_metadata.electrode_table is not None
    assert session_metadata.electrode_table[0] == 1


@pytest.mark.remote
def test_remote_dataset_converter_write_dataset_description(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003")
    dataset_converter.extract_metadata()
    dataset_converter.write_dataset_description(bids_directory=temporary_bids_directory)

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


@pytest.mark.remote
def test_remote_dataset_converter_write_subject_metadata(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003")
    dataset_converter.extract_metadata()
    dataset_converter.write_participants_metadata(bids_directory=temporary_bids_directory)

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

    expected_data_frame = pandas.DataFrame(
        {"participant_id": ["sub-123"], "species": ["Mus musculus"], "sex": ["male"]}
    )
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


@pytest.mark.remote
def test_remote_dataset_converter_write_sessions_metadata(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003")
    dataset_converter.extract_metadata()
    dataset_converter.write_sessions_metadata(bids_directory=temporary_bids_directory)

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
