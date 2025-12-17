import os
import pathlib
import typing

import pydantic


@pydantic.validate_call
def assert_subdirectory_structure(
    *,
    directory: pathlib.Path,
    expected_structure: dict[pathlib.Path, dict[typing.Literal["directories", "files"], set[str]]],
    include_hidden: bool = False,
) -> None:
    """
    Assert that the subdirectory structure matches the expected structure.

    Parameters
    ----------
    directory : directory path
        The path to the directory whose structure is to be checked.
    expected_structure : dict
        A dictionary representing the expected structure of the subdirectory.
        Keys are the full paths per expected subdirectory.
        Values are dictionaries with required 'directories' and 'files' keys whose values are sets of string names for
        all expected entities at that level.
    """
    # Future TODO: adjust to pathlib.Path.walk once 3.12 is minimum
    for dir_, directories, files in os.walk(top=directory):
        directories[:] = [d for d in directories if not d.startswith(".")]
        files = [f for f in files if not f.startswith(".")]

        dir_path = pathlib.Path(dir_)
        expected = expected_structure.get(dir_path, None)

        assert expected is not None, (
            f"\n\nUnexpected subdirectory {dir_path}.\n\n"
            f"Expected subdirectories: {list(expected_structure.keys())}\n"
        )
        assert set(expected.keys()) == {"directories", "files"}, (
            f"\n\nUnexpected keys in expected structure for {dir_path}.\n\n"
            f"Expected keys: 'directories', 'files'\n"
            f"Found keys: {set(expected.keys())}\n\n"
        )
        assert set(directories) == set(expected["directories"]), (
            f"\n\nUnexpected directories in {dir_path}.\n\n"
            f"Expected: {expected['directories']}\n"
            f"Found: {set(directories)}\n"
            f"Unexpected: {set(directories) - set(expected['directories'])}\n"
            f"Missing: {set(expected['directories']) - set(directories)}\n\n"
        )
        assert set(files) == set(expected["files"]), (
            f"\n\nUnexpected files in {dir_path}.\n\n"
            f"Expected: {expected['files']}\n"
            f"Found: {files}\n"
            f"Unexpected: {set(files) - set(expected['files'])}\n"
            f"Missing: {set(expected['files']) - set(files)}\n\n"
        )
