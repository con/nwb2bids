import json
import pathlib


def _validate_bids_directory(directory: pathlib.Path) -> pathlib.Path:
    """Validate bids_directory: if exists, must be valid BIDS; if not, parent must exist."""
    if directory.exists():
        return _validate_existing_directory_as_bids(directory)

    if not directory.parent.exists():
        raise ValueError(f"parent directory does not exist: {directory.parent}")

    return directory


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
