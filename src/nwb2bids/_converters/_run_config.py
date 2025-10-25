import json
import pathlib
import tempfile
import typing

import pydantic

from .._core._home import _get_home_directory
from .._core._run_id import _generate_run_id
from ..bids_models._base_metadata_model import MutableModel  # TODO: move this to an outer common level
from ..sanitization import SanitizationLevel


class RunConfig(MutableModel):
    """
    Specifies configuration options for a single run of NWB to BIDS conversion.

    Parameters
    ----------
    bids_directory : directory path
        The path to the directory where the BIDS dataset will be created.
        Defaults to the current working directory and checks if it is either empty or a BIDS dataset.
    sanitization_level : nwb2bids.SanitizationLevel
        Specifies the level of sanitization to apply to file and directory names when creating the BIDS dataset.
        Read more about the specific levels from `nwb2bids.sanitization.SanitizationLevel?`.
    additional_metadata_file_path : file path, optional
        The path to a YAML file containing additional metadata not included within the NWB files
        that you wish to include in the BIDS dataset.
    file_mode : one of "move", "copy", "symlink", or "auto", default: "auto"
        Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
            - "auto": Decides between all the above based on the system, with preference for linking when possible.
    cache_directory : directory path
        The directory where run specific files (e.g., notifications, sanitization reports) will be stored.
        Defaults to `~/.nwb2bids`.
    run_id : str
        On each unique run of nwb2bids, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the files saved to your run directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."
    """

    bids_directory: pydantic.DirectoryPath = pydantic.Field(default_factory=pathlib.Path.cwd)
    sanitization_level: SanitizationLevel = SanitizationLevel.NONE
    additional_metadata_file_path: pydantic.FilePath | None = None
    file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto"
    cache_directory: pydantic.DirectoryPath | None = None
    run_id: str = pydantic.Field(default_factory=_generate_run_id)

    def model_post_init(self, context: typing.Any, /) -> None:
        """Ensure the various run directories and files are created."""
        self._validate_existing_directory_as_bids()
        self._determine_file_mode()

        if self.cache_directory is None:
            self.cache_directory = _get_home_directory()
        self.parent_run_directory = self.cache_directory / "runs"
        self.parent_run_directory.mkdir(exist_ok=True)
        self.session_run_directory = self.parent_run_directory / self.run_id
        self.run_directory.mkdir(exist_ok=True)

        self.sanitization_file_path.touch()
        self.notifications_file_path.touch()
        self.notifications_json_file_path.touch()

    @pydantic.computed_field
    @property
    def sanitization_file_path(self) -> pathlib.Path:
        """The file path leading to a record of sanitizations made."""
        sanitization_file_path = self.run_directory / f"{self.run_id}_sanitization.txt"
        return sanitization_file_path

    @pydantic.computed_field
    @property
    def notifications_file_path(self) -> pathlib.Path:
        """The file path leading to a human-readable notifications report."""
        notifications_file_path = self.run_directory / f"{self.run_id}_notifications.txt"
        return notifications_file_path

    @pydantic.computed_field
    @property
    def notifications_json_file_path(self) -> pathlib.Path:
        """The file path leading to a JSON dump of the notifications."""
        notifications_file_path = self.run_directory / f"{self.run_id}_notifications.json"
        return notifications_file_path

    def _validate_existing_directory_as_bids(self) -> None:
        bids_directory = self.bids_directory

        dataset_description_file_path = bids_directory / "dataset_description.json"
        current_directory_contents = {
            path.stem for path in bids_directory.iterdir() if not path.name.startswith(".")
        } - {"README", "CHANGES", "derivatives", "dandiset"}
        if len(current_directory_contents) == 0:
            default_dataset_description = {"BIDSVersion": "1.10"}
            with dataset_description_file_path.open(mode="w") as file_stream:
                json.dump(obj=default_dataset_description, fp=file_stream, indent=4)
            return

        if not dataset_description_file_path.exists():
            message = (
                f"The directory ({bids_directory}) exists and is not empty, but is not a valid BIDS dataset: "
                "missing 'dataset_description.json'."
            )
            raise ValueError(message)

        with dataset_description_file_path.open(mode="r") as file_stream:
            dataset_description = json.load(fp=file_stream)
        if dataset_description.get("BIDSVersion", None) is None:
            message = (
                f"The directory ({bids_directory}) exists but is not a valid BIDS dataset: "
                "missing 'BIDSVersion' in 'dataset_description.json'."
            )
            raise ValueError(message)

    def _determine_file_mode(self) -> None:
        if self.file_mode != "auto":
            return

        with tempfile.TemporaryDirectory(prefix="nwb2bids-") as temp_dir_str:
            temp_dir_path = pathlib.Path(temp_dir_str)

            # Create a test file to determine if symlinks are supported
            test_file_path = temp_dir_path / "test_file.txt"
            test_file_path.touch()

            try:
                # Create a symlink to the test file
                (temp_dir_path / "test_symlink.txt").symlink_to(target=test_file_path)
            except (OSError, PermissionError, NotImplementedError):  # Windows can sometimes have trouble with symlinks
                # TODO: log a INFO message here when logging is set up
                self.file_mode = "copy"
                return
            else:
                # If symlink creation was successful, return "symlink"
                self.file_mode = "symlink"
                return
