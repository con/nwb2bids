import json
import pathlib
import typing

import pydantic

from .._core._file_mode import _determine_file_mode
from .._core._home import _get_home_directory
from .._core._run_id import _generate_run_id


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

        default_dataset_description = {"BIDSVersion": "1.10"}
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
            dataset_description = json.load(fp=file_stream)
        if dataset_description.get("BIDSVersion", None) is None:
            message = (
                f"The directory ({directory}) exists but is not a valid BIDS dataset: "
                "missing 'BIDSVersion' in 'dataset_description.json'."
            )
            raise ValueError(message)

    return directory


class RunConfig(pydantic.BaseModel):
    """
    Specifies configuration options for a single run of NWB to BIDS conversion.

    bids_directory : directory path
        The path to the directory where the BIDS dataset will be created.
        Defaults to the current working directory and checks if it is either empty or a BIDS dataset.
    additional_metadata_file_path : file path, optional
        The path to a YAML file containing additional metadata not included within the NWB files
        that you wish to include in the BIDS dataset.
    file_mode : one of "move", "copy", or "symlink"
        Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
            - if not specified, decide between all the above based on the system,
              with preference for linking when possible.
    cache_directory : directory path
        The directory where run specific files (e.g., notifications, sanitization reports) will be stored.
        Defaults to `~/.nwb2bids`.
    run_id : str
        On each unique run of nwb2bids, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the files saved to your run directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."
    """

    bids_directory: typing.Annotated[
        pydantic.DirectoryPath,
        pydantic.Field(default_factory=pathlib.Path.cwd),
        pydantic.AfterValidator(_validate_existing_directory_as_bids),
    ]
    additional_metadata_file_path: pydantic.FilePath | None = None
    file_mode: typing.Annotated[
        typing.Literal["move", "copy", "symlink"], pydantic.Field(default_factory=_determine_file_mode)
    ]
    cache_directory: typing.Annotated[pydantic.DirectoryPath, pydantic.Field(default_factory=_get_home_directory)]
    run_id: typing.Annotated[str, pydantic.Field(default_factory=_generate_run_id)]

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        validate_default=True,  # Validate default values as well
    )

    def model_post_init(self, context: typing.Any, /) -> None:

        # Ensure run directory and its parent exist
        self._parent_run_directory.mkdir(exist_ok=True)
        self._run_directory.mkdir(exist_ok=True)

        self.notifications_file_path.touch()
        self.notifications_json_file_path.touch()

    @property
    def _parent_run_directory(self) -> pathlib.Path:
        """The parent directory where all run-specific directories are stored."""
        return self.cache_directory / "runs"

    @property
    def _run_directory(self) -> pathlib.Path:
        """The directory specific to this run."""
        return self._parent_run_directory / self.run_id

    @pydantic.computed_field
    @property
    def notifications_file_path(self) -> pathlib.Path:
        """The file path leading to a human-readable notifications report."""
        notifications_file_path = self._run_directory / f"{self.run_id}_notifications.txt"
        return notifications_file_path

    @pydantic.computed_field
    @property
    def notifications_json_file_path(self) -> pathlib.Path:
        """The file path leading to a JSON dump of the notifications."""
        notifications_file_path = self._run_directory / f"{self.run_id}_notifications.json"
        return notifications_file_path
