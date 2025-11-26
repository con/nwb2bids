import pathlib

import pydantic
import pytest

import nwb2bids


def test_run_config_immutability(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    with pytest.raises(expected_exception=pydantic.ValidationError, match="Instance is frozen"):
        run_config.run_id = "new_run_id"


def test_run_config_creates_nonexistent_bids_directory(temporary_bids_directory: pathlib.Path):
    """Test that RunConfig creates the bids_directory if it doesn't exist (but parent does)."""
    nonexistent_child = temporary_bids_directory / "new_bids_dir"

    assert not nonexistent_child.exists()
    run_config = nwb2bids.RunConfig(bids_directory=nonexistent_child)
    assert nonexistent_child.exists()
    assert run_config.bids_directory == nonexistent_child


def test_run_config_missing_parent_raises(temporary_bids_directory: pathlib.Path):
    """Test that an exception is raised when parent directory doesn't exist."""
    nested_bids_directory = temporary_bids_directory / "nonexistent_parent" / "child"

    with pytest.raises(expected_exception=pydantic.ValidationError, match="parent directory does not exist"):
        nwb2bids.RunConfig(bids_directory=nested_bids_directory)
