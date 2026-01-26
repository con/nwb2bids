"""Tests for message handling passed to the top-level `converter_nwb_dataset` function."""

import json
import pathlib

import nwb2bids


def test_notifications_baseline(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)


def test_notifications_1(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_1]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    notifications = dataset_converter.notifications
    expected_notifications = [
        nwb2bids.Notification.from_definition(identifier="InvalidSpecies", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="InvalidParticipantID", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="InvalidParticipantSexBIDS", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="InvalidParticipantSexArchives", source_file_paths=nwb_paths),
    ]
    assert notifications == expected_notifications

    assert dataset_converter.run_config.notifications_json_file_path.exists()
    with dataset_converter.run_config.notifications_json_file_path.open(mode="r") as file_stream:
        notifications_json = json.load(fp=file_stream)
    str_nwb_paths = [str(path) for path in nwb_paths]
    expected_notification_json = [
        {
            "category": "SCHEMA_INVALIDATION",
            "data_standards": ["DANDI"],
            "examples": [],
            "field": "nwbfile.subject.species",
            "identifier": None,
            "reason": "Participant species is not a proper Latin binomial or NCBI " "Taxonomy id.",
            "severity": "ERROR",
            "solution": "Rename the subject species to a Latin binomial, obolibrary "
            "taxonomy link, or NCBI taxonomy reference.",
            "source_file_paths": str_nwb_paths,
            "target_file_paths": None,
            "title": "Invalid species",
        },
        {
            "category": "STYLE_SUGGESTION",
            "data_standards": ["BIDS", "DANDI"],
            "examples": ["`ab_01` -> `ab+01`", "`subject #2` -> `subject+2`", "`id 2 from 9/1/25` -> `id+2+9+1+25`"],
            "field": "nwbfile.subject.subject_id",
            "identifier": "InvalidParticipantID",
            "reason": "The participant ID contains invalid characters. BIDS allows only "
            "the plus sign to be used as a separator in the subject entity "
            "label. Underscores, dashes, spaces, slashes, and other special "
            "characters (including #) are expressly forbidden.",
            "severity": "ERROR",
            "solution": "Rename the subject without using any special characters except " "for `+`.",
            "source_file_paths": str_nwb_paths,
            "target_file_paths": None,
            "title": "Invalid participant ID",
        },
        {
            "category": "STYLE_SUGGESTION",
            "data_standards": ["BIDS"],
            "examples": ["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            "field": "nwbfile.subject.sex",
            "identifier": None,
            "reason": "Participant sex is not one of the allowed patterns by BIDS.",
            "severity": "ERROR",
            "solution": "Rename the subject sex to be one of the accepted values.",
            "source_file_paths": str_nwb_paths,
            "target_file_paths": None,
            "title": "Invalid participant sex (BIDS)",
        },
        {
            "category": "STYLE_SUGGESTION",
            "data_standards": ["DANDI"],
            "examples": ["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            "field": "nwbfile.subject.sex",
            "identifier": None,
            "reason": "Participant sex is not one of the allowed patterns by the common " "archives.",
            "severity": "ERROR",
            "solution": "Rename the subject sex to be one of the accepted values.",
            "source_file_paths": str_nwb_paths,
            "target_file_paths": None,
            "title": "Invalid participant sex (archives)",
        },
    ]
    assert notifications_json == expected_notification_json


def test_notifications_2(problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_2]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    notifications = dataset_converter.notifications
    expected_notifications = [
        nwb2bids.Notification.from_definition(identifier="MissingParticipantSex", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="MissingSpecies", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="InvalidParticipantID", source_file_paths=nwb_paths),
        nwb2bids.Notification.from_definition(identifier="InvalidSessionID", source_file_paths=nwb_paths),
    ]
    assert notifications == expected_notifications


def test_notifications_3(problematic_nwbfile_path_3: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_3]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    notifications = dataset_converter.notifications
    expected_notifications = [
        nwb2bids.Notification.from_definition(identifier="MissingParticipant", source_file_paths=nwb_paths),
    ]
    assert notifications == expected_notifications


def test_notifications_4(problematic_nwbfile_path_4: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_4]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    notifications = dataset_converter.notifications
    expected_notifications = [
        nwb2bids.Notification.from_definition(
            identifier="MissingDescription",
            # source_file_paths=nwb_paths  # TODO: figure out better way of handling here
        ),
    ]
    assert notifications == expected_notifications
