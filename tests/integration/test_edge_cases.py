"""
Integration tests for edge cases of the primary `convert_nwb_dataset` function.

Namely, the cases of:
  - A dataset with additional metadata and the case of a dataset.
  - A dataset without a session ID.
"""

import pathlib

import pandas

import nwb2bids


def test_convert_nwb_dataset_with_additional_metadata(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    additional_metadata_file_path: pathlib.Path,
):
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(
        bids_directory=temporary_bids_directory, additional_metadata_file_path=additional_metadata_file_path
    )
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_convert_nwb_dataset_on_mock_datalad_dataset(
    mock_datalad_dataset: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [mock_datalad_dataset]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    notifications = converter.messages

    errors = [notification for notification in notifications if notification.severity == nwb2bids.Severity.ERROR]
    assert len(errors) == 0, f"Errors were raised during conversion: {errors}"

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_convert_nwb_dataset_on_mock_datalad_dataset_with_broken_symlink(
    mock_datalad_dataset: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    broken_symlink = mock_datalad_dataset / "broken_symlink.nwb"
    broken_symlink.symlink_to(target="non_existent_file.nwb")
    nwb_paths = [mock_datalad_dataset]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    notifications = converter.messages

    errors = [notification for notification in notifications if notification.severity == nwb2bids.Severity.ERROR]
    assert len(errors) == 0, f"Errors were raised during conversion: {errors}"

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )


def test_convert_nwb_dataset_with_subject_mismatch(
    minimal_nwbfile_path: pathlib.Path,
    minimal_mismatch_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    nwb_paths = [minimal_nwbfile_path, minimal_mismatch_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert len(converter.messages) == 1

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-456", "ses-4567"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-456"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-456_ecephys.nwb"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-4567": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-4567"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-4567_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    participants_tsv_file_path = temporary_bids_directory / "participants.tsv"
    actual_dataframe = pandas.read_csv(filepath_or_buffer=participants_tsv_file_path, sep="\t")
    expected_dataframe = pandas.DataFrame(
        {"participant_id": {0: "sub-123"}, "species": {0: "Mus musculus, mouse"}, "sex": {0: "M"}}
    )
    pandas.testing.assert_frame_equal(left=actual_dataframe, right=expected_dataframe)
