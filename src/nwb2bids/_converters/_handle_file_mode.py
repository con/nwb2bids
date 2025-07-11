import pathlib
import shutil
import tempfile
import typing


def _handle_file_mode(
    file_mode: typing.Literal["move", "copy", "symlink"] | None = None,
) -> typing.Literal["move", "copy", "symlink"]:
    if file_mode is not None:
        return file_mode

    try:
        test_directory = pathlib.Path(tempfile.mkdtemp(prefix="nwb2bids-"))
        test_file_path = test_directory / "test_file.txt"
        test_file_path.touch()
        (test_directory / "test_symlink.txt").symlink_to(target=test_file_path)
        shutil.rmtree(path=test_directory, ignore_errors=True)
        return "symlink"
    except (OSError, PermissionError):  # Windows can sometimes have trouble with symlinks
        return "copy"
