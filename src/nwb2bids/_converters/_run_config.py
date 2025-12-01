import pathlib
import typing

import pydantic

from .._core._file_mode import _determine_file_mode
from .._core._home import _get_home_directory
from .._core._run_id import _generate_run_id
from .._core._validate_existing_bids import _validate_bids_directory
from ..sanitization import SanitizationLevel


class RunConfig(pydantic.BaseModel):
    """
    Specifies configuration options for a single run of NWB to BIDS conversion.

    bids_directory : directory path
        The path to the directory where the BIDS dataset will be created.
        Defaults to the current working directory and checks if it is either empty or a BIDS dataset.
    sanitization_level : nwb2bids.SanitizationLevel
        Specifies the level of sanitization to apply to file and directory names when creating the BIDS dataset.
        Read more about the specific levels from `nwb2bids.sanitization.SanitizationLevel?`.
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
        pathlib.Path,
        pydantic.Field(default_factory=pathlib.Path.cwd),
        pydantic.AfterValidator(_validate_bids_directory),
    ]
    additional_metadata_file_path: pydantic.FilePath | None = None
    file_mode: typing.Annotated[
        typing.Literal["move", "copy", "symlink"], pydantic.Field(default_factory=_determine_file_mode)
    ]
    cache_directory: typing.Annotated[pydantic.DirectoryPath, pydantic.Field(default_factory=_get_home_directory)]
    sanitization_level: SanitizationLevel = SanitizationLevel.NONE
    run_id: typing.Annotated[str, pydantic.Field(default_factory=_generate_run_id)]
    _parent_run_directory: pathlib.Path = pydantic.PrivateAttr()
    _run_directory: pathlib.Path = pydantic.PrivateAttr()

    model_config = pydantic.ConfigDict(
        frozen=True,  # Make the model immutable
        validate_default=True,  # Validate default values as well
    )

    def model_post_init(self, context: typing.Any, /) -> None:
        self._parent_run_directory = self.cache_directory / "runs"
        self._run_directory = self._parent_run_directory / self.run_id

        # Ensure run directory and its parent exist
        self._parent_run_directory.mkdir(exist_ok=True)
        self._run_directory.mkdir(exist_ok=True)

        self.sanitization_file_path.touch()
        self.notifications_file_path.touch()
        self.notifications_json_file_path.touch()

    @pydantic.computed_field
    @property
    def sanitization_file_path(self) -> pathlib.Path:
        """The file path leading to a record of sanitizations made."""
        sanitization_file_path = self._run_directory / f"{self.run_id}_sanitization.txt"
        return sanitization_file_path

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
