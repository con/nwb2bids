import pathlib

import pydantic
import pytest

import nwb2bids


def test_run_config_immutability(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    with pytest.raises(expected_exception=pydantic.ValidationError, match="Instance is frozen"):
        run_config.run_id = "new_run_id"


def test_run_config_accepts_nonexistent_bids_directory(temporary_bids_directory: pathlib.Path):
    """Test that RunConfig accepts a nonexistent bids_directory if parent exists (but doesn't create it)."""
    nonexistent_child = temporary_bids_directory / "new_bids_dir"

    assert not nonexistent_child.exists()
    run_config = nwb2bids.RunConfig(bids_directory=nonexistent_child)
    assert not nonexistent_child.exists()  # NOT created at init time
    assert run_config.bids_directory == nonexistent_child


def test_run_config_missing_parent_raises(temporary_bids_directory: pathlib.Path):
    """Test that an exception is raised when parent directory doesn't exist."""
    nested_bids_directory = temporary_bids_directory / "nonexistent_parent" / "child"

    with pytest.raises(
        expected_exception=pydantic.ValidationError,
        match=r"The parent path \(\S+\) does not exist",
    ):
        nwb2bids.RunConfig(bids_directory=nested_bids_directory)


def test_run_config_file_path_as_bids_directory(temporary_bids_directory: pathlib.Path):
    """Test that an exception is raised when a path pointing to a file is given as bids_directory."""
    file_path = temporary_bids_directory / "some_file.txt"
    file_path.touch()

    with pytest.raises(
        expected_exception=pydantic.ValidationError,
        match=r"The path \(\S+\) exists but is not a directory",
    ):
        nwb2bids.RunConfig(bids_directory=file_path)


def test_run_config_file_path_as_bids_directory_parent(temporary_bids_directory: pathlib.Path):
    """Test that an exception is raised when a path with its parent pointing to a file is given as bids_directory."""
    file_path = temporary_bids_directory / "some_file.txt"
    file_path.touch()
    bids_directory = file_path / "child_directory"

    with pytest.raises(
        expected_exception=pydantic.ValidationError,
        match=r"The parent path \(\S+\) exists but is not a directory",
    ):
        nwb2bids.RunConfig(bids_directory=bids_directory)
