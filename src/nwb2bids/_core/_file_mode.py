import pathlib
import tempfile
import typing


def _determine_file_mode() -> typing.Literal["symlink", "copy"]:
    """
    Determine what file mode to use in creating a BIDS dataset based on the system
    """
    with tempfile.TemporaryDirectory(prefix="nwb2bids-") as temp_dir_str:
        temp_dir_path = pathlib.Path(temp_dir_str)

        # Create a test file to determine if symlinks are supported
        test_file_path = temp_dir_path / "test_file.txt"
        test_file_path.touch()

        try:
            # Create a symlink to the test file
            (temp_dir_path / "test_symlink.txt").symlink_to(target=test_file_path)
        except (OSError, PermissionError, NotImplementedError):  # Windows can sometimes have trouble with symlinks
            # TODO: log a INFO message here when logging is set up
            return "copy"
        else:
            # If symlink creation was successful, return "symlink"
            return "symlink"
