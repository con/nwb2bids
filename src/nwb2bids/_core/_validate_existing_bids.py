import json
import pathlib


def _validate_bids_directory(path: pathlib.Path) -> pathlib.Path:
    """
    Validate that a given path points to a BIDS directory

    The given path is considered valid if:

    - it points to an existing BIDS directory, which contains a valid `dataset_description.json` file.
    - it points to an empty directory, in which case a minimal `dataset_description.json` file will be
      created and added to the directory.
    - it does not point to an object in the file system, but its parent exists as a directory.

    Parameters
    ----------
    path : pathlib.Path
        The path to validate as a BIDS directory.

    Returns
    -------
    pathlib.Path
        The validated BIDS directory path.

    Raises
    ------
    ValueError
        If the given path is not valid according to the criteria above (as this function
        is designed to be used as a field validator for a pydantic model).
    """

    if path.is_dir():
        return _validate_existing_directory_as_bids(path)
    if path.exists():
        raise ValueError(f"The path ({path}) exists but is not a directory.")
    if not path.parent.is_dir():
        if not path.parent.exists():
            raise ValueError(f"The parent path ({path.parent}) does not exist.")
        raise ValueError(f"The parent path ({path.parent}) exists but is not a directory.")

    return path


def _validate_existing_directory_as_bids(directory: pathlib.Path) -> pathlib.Path:

    dataset_description_file_path = directory / "dataset_description.json"
    current_directory_contents = {path.stem for path in directory.iterdir() if not path.name.startswith(".")} - {
        "README",
        "CHANGES",
        "derivatives",
        "dandiset",
    }

    if len(current_directory_contents) == 0:
        # The directory is considered empty, not containing any meaningful content.
        # Populate the directory with `dataset_description.json` to make it
        # a valid (though minimal) BIDS dataset.

        default_dataset_description = {"BIDSVersion": "1.10", "HEDVersion": "8.3.0"}
        with dataset_description_file_path.open(mode="w") as file_stream:
            json.dump(obj=default_dataset_description, fp=file_stream, indent=4)
    else:
        # The directory is considered non-empty

        if not dataset_description_file_path.is_file():
            # The directory is without `dataset_description.json` file
            # It is an invalid BIDS dataset.

            message = (
                f"The directory ({directory}) exists and is not empty, but is not a valid BIDS dataset: "
                "missing 'dataset_description.json' file."
            )
            raise ValueError(message)

        with dataset_description_file_path.open(mode="r") as file_stream:
            try:
                dataset_description = json.load(fp=file_stream)
            except json.JSONDecodeError as exception:
                message = (
                    f"The directory ({directory}) exists and contains a 'dataset_description.json' file, "
                    "but it is not a valid JSON file."
                )
                raise ValueError(message) from exception

        if not isinstance(dataset_description, dict):
            message = (
                f"The directory ({directory}) exists and contains a 'dataset_description.json' file, "
                "but it does not contain a valid JSON object."
            )
            raise ValueError(message)
        if dataset_description.get("BIDSVersion", None) is None:
            message = (
                f"The directory ({directory}) exists but is not a valid BIDS dataset: "
                "missing 'BIDSVersion' in 'dataset_description.json'."
            )
            raise ValueError(message)

    return directory
