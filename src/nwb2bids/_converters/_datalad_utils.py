import os
import pathlib


def _read_first_bytes(file_path: pathlib.Path, n: int = 6) -> bytes:
    """
    Read the first n (by default 6) bytes of a file; necessary for Windows 'symlinks'.
    """
    with file_path.open(mode="rb") as file_stream:
        first_bytes = file_stream.read(n)
        return first_bytes


def _content_is_retrieved(file_path: pathlib.Path) -> bool:
    """
    Check if a file contents are fetched from the git-annex.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.

    Returns
    -------
    bool
        True if the file is a pointer to annex contents, False otherwise.
    """
    if not file_path.exists():
        return False

    if file_path.is_symlink():
        if file_path.stat().st_size > 1024:  # No currently annexed file can be larger than this
            return True
        if "/annex" not in os.readlink(path=file_path):
            return True
        return file_path.resolve().exists()

    return _read_first_bytes(file_path=file_path, n=6) != b"/annex"
