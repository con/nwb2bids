"""Unit tests for the notification dump feature."""

import json
import pathlib

import nwb2bids


def test_run_config_creates_notification_directory(temporary_bids_directory: pathlib.Path):
    """Test that RunConfig creates the .nwb2bids directory and subdirectory."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    # Check that .nwb2bids directory was created
    nwb2bids_directory = temporary_bids_directory / ".nwb2bids"
    assert nwb2bids_directory.exists()
    assert nwb2bids_directory.is_dir()

    # Check that run-specific subdirectory was created
    run_directory = nwb2bids_directory / run_config.run_id
    assert run_directory.exists()
    assert run_directory.is_dir()


def test_run_config_creates_notification_files(temporary_bids_directory: pathlib.Path):
    """Test that RunConfig creates the notification files."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    # Check that notification files were created
    notifications_txt_path = run_config.notifications_file_path
    notifications_json_path = run_config.notifications_json_file_path

    assert notifications_txt_path.exists()
    assert notifications_json_path.exists()


def test_notifications_file_path_format(temporary_bids_directory: pathlib.Path):
    """Test that notification file paths have the correct format."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    # Check text file path
    notifications_txt_path = run_config.notifications_file_path
    expected_txt_name = f"{run_config.run_id}_notifications.txt"
    assert notifications_txt_path.name == expected_txt_name
    assert notifications_txt_path.parent.name == run_config.run_id

    # Check JSON file path
    notifications_json_path = run_config.notifications_json_file_path
    expected_json_name = f"{run_config.run_id}_notifications.json"
    assert notifications_json_path.name == expected_json_name
    assert notifications_json_path.parent.name == run_config.run_id


def test_notifications_json_dump_content(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    """Test that notification JSON dump contains valid inspection results."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    assert notifications_json_path.exists()

    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # Check that it's a list
    assert isinstance(notifications_data, list)

    # Check that the number of notifications matches
    assert len(notifications_data) == len(converter.messages)

    # If there are notifications, validate the structure
    if len(notifications_data) > 0:
        first_notification = notifications_data[0]

        # Check required fields
        assert "title" in first_notification
        assert "reason" in first_notification
        assert "solution" in first_notification
        assert "category" in first_notification
        assert "severity" in first_notification

        # Check that enum values are serialized as names (strings)
        assert isinstance(first_notification["category"], str)
        assert isinstance(first_notification["severity"], str)


def test_notifications_json_dump_enums_serialized(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test that enum values in notifications are properly serialized as strings."""
    nwb_paths = [minimal_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # Verify enum fields are strings (not integers or objects)
    for notification in notifications_data:
        if "category" in notification:
            assert isinstance(notification["category"], str)
            # Should be one of the Category enum names
            assert notification["category"] in ["STYLE_SUGGESTION", "SCHEMA_INVALIDATION", "INTERNAL_ERROR"]

        if "severity" in notification:
            assert isinstance(notification["severity"], str)
            # Should be one of the Severity enum names
            assert notification["severity"] in ["INFO", "HINT", "WARNING", "ERROR", "CRITICAL"]

        if "data_standards" in notification and notification["data_standards"] is not None:
            for standard in notification["data_standards"]:
                assert isinstance(standard, str)
                # Should be one of the DataStandard enum names
                assert standard in ["DANDI", "HED", "NWB", "BIDS"]


def test_multiple_runs_create_separate_directories(temporary_bids_directory: pathlib.Path):
    """Test that multiple runs create separate subdirectories in .nwb2bids."""
    # Create first run config
    run_config_1 = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    run_id_1 = run_config_1.run_id

    # Create second run config (will have different run_id due to timestamp)
    import time

    time.sleep(1.1)  # Ensure different timestamp (run_id uses second precision)
    run_config_2 = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    run_id_2 = run_config_2.run_id

    # Verify different run IDs
    assert run_id_1 != run_id_2

    # Check that both subdirectories exist
    nwb2bids_directory = temporary_bids_directory / ".nwb2bids"
    assert (nwb2bids_directory / run_id_1).exists()
    assert (nwb2bids_directory / run_id_2).exists()


def test_notification_dump_with_ecephys_data(
    ecephys_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """Test notification dump with ecephys data that may generate warnings."""
    nwb_paths = [ecephys_nwbfile_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    # Read the notifications JSON file
    notifications_json_path = run_config.notifications_json_file_path
    assert notifications_json_path.exists()

    with notifications_json_path.open(mode="r") as file_stream:
        notifications_data = json.load(fp=file_stream)

    # Verify it's valid JSON and a list
    assert isinstance(notifications_data, list)
    assert len(notifications_data) == len(converter.messages)
