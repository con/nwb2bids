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

    # Note that if the file path is a 'broken' symlink (the target does not exist)
    # the call to `.exists()` would actually return False
    if file_path.is_symlink() and ('.git' in file_path.readlink().parts):
        return True

    return _read_first_bytes(file_path=file_path, n=6) != b"/annex"
