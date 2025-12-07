"""Integration tests for the notification dump feature during conversion."""

import json
import pathlib

import pytest

import nwb2bids


def test_notification_dump_in_bids_directory_structure(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that the .nwb2bids directory is created in the BIDS output directory."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Verify .nwb2bids directory is in BIDS directory
    nwb2bids_directory = temporary_bids_directory / ".nwb2bids"
    assert nwb2bids_directory.exists()
    assert nwb2bids_directory.is_dir()

    # Verify run-specific subdirectory exists
    run_subdirectories = list(nwb2bids_directory.iterdir())
    assert len(run_subdirectories) >= 1
    assert all(subdir.is_dir() for subdir in run_subdirectories)


def test_notification_files_created_after_conversion(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that notification files exist after conversion completes."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Check that notification files were created
    notifications_txt_path = run_config.notifications_file_path
    notifications_json_path = run_config.notifications_json_file_path

    assert notifications_txt_path.exists()
    assert notifications_json_path.exists()

    # Verify JSON file has content (at minimum an empty list)
    with notifications_json_path.open(mode="r") as file_stream:
        content = file_stream.read()
        assert len(content) > 0


def test_notification_dump_with_multiple_sessions(
    testing_files_directory: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test notification dump with multiple NWB sessions."""
    # Create multiple test NWB files
    from tests.conftest import _make_minimal_nwbfile
    import pynwb

    session_paths = []
    for session_index in range(3):
        nwbfile = _make_minimal_nwbfile(session_id=f"session-{session_index}")
        file_path = testing_files_directory / f"test_multi_{session_index}.nwb"

        with pynwb.NWBHDF5IO(path=file_path, mode="w") as io:
            io.write(nwbfile)
        session_paths.append(file_path)

    # Run conversion
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=session_paths, run_config=run_config)

    # Verify notification dump exists and has content
    notifications_json_path = run_config.notifications_json_file_path
    assert notifications_json_path.exists()

    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    assert isinstance(notifications_data, list)
    # Should match the number of messages from converter
    assert len(notifications_data) == len(converter.messages)


def test_notification_dump_persists_inspection_results(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that inspection results are properly persisted to the notification dump."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Get messages from converter
    converter_messages = converter.messages

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # Verify count matches
    assert len(notifications_data) == len(converter_messages)

    # Verify each message is properly serialized
    for converter_msg, json_msg in zip(converter_messages, notifications_data):
        assert json_msg["title"] == converter_msg.title
        assert json_msg["reason"] == converter_msg.reason
        assert json_msg["solution"] == converter_msg.solution
        assert json_msg["category"] == converter_msg.category.name
        assert json_msg["severity"] == converter_msg.severity.name


def test_notification_dump_includes_all_message_fields(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that all InspectionResult fields are included in the JSON dump."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # If there are notifications, check they have all expected fields
    if len(notifications_data) > 0:
        notification = notifications_data[0]
        
        # Required fields
        assert "title" in notification
        assert "reason" in notification
        assert "solution" in notification
        assert "category" in notification
        assert "severity" in notification
        
        # Optional fields should be present (even if None)
        assert "examples" in notification
        assert "field" in notification
        assert "source_file_paths" in notification
        assert "target_file_paths" in notification
        assert "data_standards" in notification


def test_notification_dump_with_conversion_errors(
    problematic_nwbfile_path_missing_session_id: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test notification dump when conversion encounters issues."""
    nwb_paths = [problematic_nwbfile_path_missing_session_id]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    assert notifications_json_path.exists()

    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # Should have notifications for the missing session ID issue
    assert len(notifications_data) >= 1
    assert len(notifications_data) == len(converter.messages)


def test_hidden_nwb2bids_directory_not_in_bids_structure(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that .nwb2bids directory doesn't interfere with BIDS structure validation."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # The .nwb2bids directory should exist
    nwb2bids_directory = temporary_bids_directory / ".nwb2bids"
    assert nwb2bids_directory.exists()

    # But normal BIDS files should also exist
    dataset_description_path = temporary_bids_directory / "dataset_description.json"
    assert dataset_description_path.exists()

    participants_tsv_path = temporary_bids_directory / "participants.tsv"
    assert participants_tsv_path.exists()


def test_notification_dump_json_is_valid_json(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that the notification dump produces valid, parseable JSON."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    notifications_json_path = run_config.notifications_json_file_path

    # Should be able to parse without errors
    try:
        with notifications_json_path.open(mode="r") as file_stream:
            notifications_data = json.load(fp=file_stream)
        
        # Should be a list
        assert isinstance(notifications_data, list)
        
        # Can be serialized back to JSON without errors
        json.dumps(notifications_data)
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON file is not valid: {e}")
