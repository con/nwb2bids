"""
Integration tests for edge cases of the primary `convert_nwb_dataset` function.

Namely, the cases of:
  - A dataset with additional metadata and the case of a dataset.
  - A dataset without a session ID.
"""

import os
import pathlib

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


def test_symlink_resolves_correctly_with_relative_path(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that symlinks created from relative paths resolve to the correct target."""
    # Change to the parent directory and use a relative path to the NWB file
    original_cwd = os.getcwd()
    try:
        os.chdir(minimal_nwbfile_path.parent)
        relative_nwb_path = pathlib.Path(minimal_nwbfile_path.name)

        nwb_paths = [relative_nwb_path]
        run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, file_mode="symlink")
        nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

        symlink_path = temporary_bids_directory / "sub-123" / "ses-456" / "ecephys" / "sub-123_ses-456_ecephys.nwb"

        assert symlink_path.is_symlink(), "Expected a symlink to be created"
        assert symlink_path.resolve() == minimal_nwbfile_path.resolve(), "Symlink does not resolve to original file"
        assert os.path.exists(symlink_path), "Symlink is broken (target does not exist)"
    finally:
        os.chdir(original_cwd)
