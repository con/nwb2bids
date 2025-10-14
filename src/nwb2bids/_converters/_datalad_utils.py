import os
import pathlib


def is_file_annexed(file_path: pathlib.Path) -> bool:
    """
    Check if a file contents are not fetched from the git-annex.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.

    Returns
    -------
    bool
        True if the file is a pointer to annex contents, False otherwise.
    """
    # Unix systems
    if file_path.is_symlink() and os.readlink(file_path).startswith("/annex"):
        return True

    # Windows may require manual introspection
    with file_path.open(mode="rb") as file_stream:
        first_bytes = file_stream.read(6)
        is_annexed = first_bytes == b"/annex"
        return is_annexed
