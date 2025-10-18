import pathlib

import pydantic


@pydantic.validate_call
def create_file_tree(directory: pathlib.Path, structure: dict[str, dict | str]) -> None:
    """
    Creates a directory and file tree based on a dictionary structure.

    Each key in the dictionary represents a file or directory name.
    If the value is a dictionary, it represents a subdirectory with its own structure.
    If the value is a string, the key is taken to represent a file with this value as its content.

    Parameters
    ----------
    directory : pathlib.Path
        The root directory where the tree will be created.
    structure : dict
        A nested dictionary representing the directory and file structure.
    """
    for key, value in structure.items():
        subpath = directory / key
        if isinstance(value, dict):
            subpath.mkdir(exist_ok=True)
            create_file_tree(directory=subpath, structure=value)
        elif isinstance(value, str):
            subpath.write_text(data=value)
