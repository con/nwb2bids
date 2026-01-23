import pathlib


def _file_startswith(file_path: pathlib.Path, s: str) -> bool:
    """
    Check if a file starts with a specific string; necessary for Windows 'symlinks'.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.
    s : str
        String to check if the file starts with.

    Returns
    -------
    bool
        True if the file starts with the given string, False otherwise.
    """
    with file_path.open(mode="rb") as file_stream:
        first_bytes = file_stream.read(len(s))
        return first_bytes == s.encode("utf-8")


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
    if file_path.is_symlink() and (".git" in file_path.readlink().parts):
        return True

    return not _file_startswith(file_path=file_path, s="/annex")
