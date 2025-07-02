import json
import pathlib

import pandas

import nwb2bids


def test_dataset_converter_initialization(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)


def test_dataset_converter_metadata_extraction(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    dataset_converter.extract_dataset_metadata()

    expected_dataset_metadata = nwb2bids.models.BidsDatasetMetadata(
        sessions_metadata=[
            nwb2bids.models.BidsSessionMetadata(
                session_id="20240309",
                subject=nwb2bids.models.Subject(participant_id="123", species="Mus musculus", sex="male"),
                extra={
                    "session": {"session_id": "20240309", "number_of_trials": None, "comments": "session_description"},
                    "general_ephys": {"InstitutionName": None},
                    "subject": {"participant_id": "123", "species": "Mus musculus", "strain": None, "sex": "male"},
                    "probes": [],
                },
            )
        ]
    )
    assert dataset_converter.dataset_metadata == expected_dataset_metadata


def test_dataset_converter_write_dataset_description(
    minimal_nwbfile_path: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(
        nwb_directory=minimal_nwbfile_path.parent, additional_metadata_file_path=additional_metadata_file_path
    )
    dataset_converter.extract_dataset_metadata()
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


def test_dataset_converter_write_subject_metadata(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    dataset_converter.extract_dataset_metadata()
    dataset_converter.write_participants_metadata(bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {"directories": set(), "files": {"participants.json", "participants.tsv"}}
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
        "participant_id": "A unique participant identifier for this subject.",
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
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    dataset_converter.extract_dataset_metadata()
    dataset_converter.write_sessions_metadata(bids_directory=temporary_bids_directory)

    expected_structure = {
        temporary_bids_directory: {"directories": {"sub-123"}, "files": set()},
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-20240309"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-20240309": {
            "directories": set(),
            "files": set(),
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    sessions_tsv_file_path = temporary_bids_directory / "sub-123" / "sub-123_sessions.tsv"
    sessions_data_frame = pandas.read_csv(filepath_or_buffer=sessions_tsv_file_path, sep="\t", dtype=str)

    expected_data_frame = pandas.DataFrame({"session_id": ["ses-20240309"]})
    pandas.testing.assert_frame_equal(left=sessions_data_frame, right=expected_data_frame)

    sessions_json_file_path = temporary_bids_directory / "sub-123" / "sub-123_sessions.json"
    with sessions_json_file_path.open(mode="r") as file_stream:
        sessions_json = json.load(fp=file_stream)
    expected_sessions_json = {"session_id": "A unique session identifier."}
    assert sessions_json == expected_sessions_json
