import pathlib

import pydantic
import pytest

import nwb2bids


def test_run_config_immutability(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    with pytest.raises(expected_exception=pydantic.ValidationError, match="Instance is frozen"):
        run_config.run_id = "new_run_id"  # type: ignore[misc]


def test_rejected_nonexistent_bids_directory(temporary_bids_directory: pathlib.Path):
    """Test that RunConfig rejects a nonexistent bids_directory, even if its parent exists."""
    nonexistent_child = temporary_bids_directory / "new_bids_dir"

    assert not nonexistent_child.exists()
    with pytest.raises(
        expected_exception=pydantic.ValidationError,
        match=r"The path \(\S+\) does not exist",
    ):
        nwb2bids.RunConfig(bids_directory=nonexistent_child)


def test_run_config_missing_parent_raises(temporary_bids_directory: pathlib.Path):
    """Test that an exception is raised when parent directory doesn't exist."""
    nested_bids_directory = temporary_bids_directory / "nonexistent_parent" / "child"

    with pytest.raises(
        expected_exception=pydantic.ValidationError,
        match=r"The path \(\S+\) does not exist",
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
        match=r"The path \(\S+\) does not exist",
    ):
        nwb2bids.RunConfig(bids_directory=bids_directory)


def test_run_config_archive_target_default_is_none(temporary_bids_directory: pathlib.Path):
    """Test that the archive_target field defaults to None."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    assert run_config.archive_target is None


@pytest.mark.parametrize("archive_target", ["dandi", "ember"])
def test_run_config_archive_target_valid_values(temporary_bids_directory: pathlib.Path, archive_target: str):
    """Test that archive_target accepts valid values."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, archive_target=archive_target)
    assert run_config.archive_target == archive_target


def test_run_config_archive_target_invalid_value_raises(temporary_bids_directory: pathlib.Path):
    """Test that archive_target rejects invalid values."""
    with pytest.raises(expected_exception=pydantic.ValidationError):
        nwb2bids.RunConfig(bids_directory=temporary_bids_directory, archive_target="invalid")
