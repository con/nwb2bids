"""
Integration tests for the session label logic.

Tests the following rules:
- Single-session subjects do NOT use `ses-` labels.
- Multi-session subjects (>1 session per subject) ALWAYS use `ses-` labels.
- If >50% of all subjects have multiple sessions, ALL subjects use `ses-` labels
  (dataset-level consistency rule).
"""

import pathlib

import nwb2bids


def test_single_session_subject_no_ses_label(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """A single-session subject should NOT have `ses-` labels in file names or directory structure."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

    # No ses- directory, file directly under sub-123/ecephys/
    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    # Verify session converter has use_session_labels=False
    assert len(dataset_converter.session_converters) == 1
    assert dataset_converter.session_converters[0].use_session_labels is False


def test_multi_session_subject_uses_ses_labels(
    directory_with_multiple_nwbfiles: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """A subject with multiple sessions should use `ses-` labels."""
    nwb_paths = [directory_with_multiple_nwbfiles]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    # Note: session IDs like "session-0" may generate style notifications, which is acceptable here

    # ses- directories present for each session of subject 123
    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-123": {
            "directories": {"ses-session-0", "ses-session-1"},
            "files": {"sub-123_sessions.json", "sub-123_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-0": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-0"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-session-0_ecephys.nwb"},
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-1": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-123"
        / "ses-session-1"
        / "ecephys": {
            "directories": set(),
            "files": {"sub-123_ses-session-1_ecephys.nwb"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )

    # All session converters should have use_session_labels=True
    assert all(sc.use_session_labels is True for sc in dataset_converter.session_converters)


def test_majority_multi_session_applies_ses_labels_globally(
    directory_with_mixed_session_counts: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """
    When >50% of subjects have multiple sessions, ALL subjects use `ses-` labels.

    subX: 2 sessions (X1, X2), subY: 2 sessions (Y1, Y2) (both multi-session)
    subZ: 1 session (Z1) (single-session, but gets ses- label due to >50% rule)
    2/3 = 66.7% subjects have multiple sessions -> global ses- labels applied.
    """
    nwb_paths = [directory_with_mixed_session_counts]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

    # All subjects should use ses- labels, including single-session subZ
    assert all(sc.use_session_labels is True for sc in dataset_converter.session_converters)

    # Verify subZ has ses- structure even though it only has one session
    # (50% rule: 2/3 = 66.7% of subjects have multiple sessions, which is >50%)
    expected_subZ_session_directory = temporary_bids_directory / "sub-subZ" / "ses-Z1"
    assert expected_subZ_session_directory.exists()
    expected_subZ_file = expected_subZ_session_directory / "ecephys" / "sub-subZ_ses-Z1_ecephys.nwb"
    assert expected_subZ_file.exists()

    # Verify subX has ses- structure for both sessions
    expected_subX_session1 = temporary_bids_directory / "sub-subX" / "ses-X1"
    expected_subX_session2 = temporary_bids_directory / "sub-subX" / "ses-X2"
    assert expected_subX_session1.exists()
    assert expected_subX_session2.exists()


def test_set_use_session_labels_single_subject_single_session(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Unit test for _set_use_session_labels with a single-session subject."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()
    dataset_converter._set_use_session_labels()

    assert len(dataset_converter.session_converters) == 1
    assert dataset_converter.session_converters[0].use_session_labels is False


def test_set_use_session_labels_single_subject_multi_session(
    directory_with_multiple_nwbfiles: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Unit test for _set_use_session_labels with a multi-session single subject."""
    nwb_paths = [directory_with_multiple_nwbfiles]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=nwb_paths, run_config=run_config)
    dataset_converter.extract_metadata()
    dataset_converter._set_use_session_labels()

    assert len(dataset_converter.session_converters) == 2
    assert all(sc.use_session_labels is True for sc in dataset_converter.session_converters)


def test_force_session_labels_overrides_single_session_default(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """With force_session_labels=True, a single-session subject still gets `ses-` labels."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, force_session_labels=True)
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(dataset_converter.notifications)

    # ses- directory present even though only one session exists
    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-123"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
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

    assert len(dataset_converter.session_converters) == 1
    assert dataset_converter.session_converters[0].use_session_labels is True
