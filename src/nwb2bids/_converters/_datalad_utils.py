import os
import pathlib
import platform


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
    # On Windows, symlinks are supported indirectly; files begin with "/annex/..."
    # then `datalad get` replaces the original file with the retrieved content
    if platform.system() == "Windows" and _read_first_bytes(file_path=file_path) == b"/annex":
        return False

    is_symlink = file_path.is_symlink()
    if not is_symlink:
        return True

    linked_path = os.readlink(path=file_path)
    if "/annex" not in linked_path:
        return True

    file_exists = file_path.resolve().exists()
    return file_exists
