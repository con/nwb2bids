import datetime
import pathlib
import typing

import pydantic

from .._core._file_mode import _determine_file_mode
from .._core._global_config import _load_run_config_defaults
from .._core._home import _get_nwb2bids_home_directory
from .._core._validate_existing_bids import _validate_bids_directory
from ..sanitization import SanitizationConfig


def _generate_run_id() -> str:
    """
    Generate a unique run ID based on the current date and time.

    Returns
    -------
    run_id : str
        On each unique run of `nwb2bids`, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the notification and sanitization reports saved to your cache directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."
    """
    run_id = datetime.datetime.now().strftime("datetime-%Y%m%d%H%M%S")
    return run_id


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
              Copy-on-write is supported and used on systems that allow it, but requires Python 3.14 to use.
            - "symlink": Create symbolic links to the files in the BIDS directory.
            - if not specified, decide between all the above based on the system,
              with preference for linking when possible.
    cache_directory : directory path
        The directory where run specific files (e.g., notifications, sanitization reports) will be stored.
        Defaults to `~/.nwb2bids`.
    sanitization_config : nwb2bids.SanitizationConfig
        Specifies the types of sanitization to apply when creating the BIDS dataset.
        Read more about the specific options from `nwb2bids.sanitization.SanitizationConfig?`.
    run_id : str
        On each unique run of nwb2bids, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the files saved to your run directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."
    archive_target : one of "dandi", "ember", or None, default: None
        The archive you intend to upload the BIDS dataset to.
        When set to a non-`None` value, a `.bidsignore` file is created in the BIDS directory
        containing `dandiset.yaml`, since `dandiset.yaml` is not part of the BIDS specification.
        If `None`, then no `.bidsignore` file is created.
    use_session_labels : bool, default: False
        When `True`, `ses-` labels and session-level subdirectories are always included in BIDS output,
        even when every subject has only a single session.
        By default (`False`), `ses-` labels are omitted for single-session subjects unless more than 50% of
        subjects have multiple sessions, in which case they are applied to all subjects for dataset-level
        consistency.
    silent : bool, default: False
        Whether to suppress progress bar output during conversion.
        Set to ``True`` to hide all progress bars (e.g., when ``--silent`` is used via the CLI).
    """

    bids_directory: pathlib.Path = pydantic.Field(default_factory=pathlib.Path.cwd)
    additional_metadata_file_path: pydantic.FilePath | None = None
    file_mode: typing.Literal["move", "copy", "symlink"] = pydantic.Field(default_factory=_determine_file_mode)
    cache_directory: pydantic.DirectoryPath = pydantic.Field(default_factory=_get_nwb2bids_home_directory)
    sanitization_config: SanitizationConfig = pydantic.Field(default_factory=SanitizationConfig)
    run_id: str = pydantic.Field(default_factory=_generate_run_id)
    space: typing.Literal["AllenCCFv3", "PaxinosWatson"] | None = pydantic.Field(
        default=None,
        description=(
            "The atlas/coordinate space label to apply to electrode positions. "
            "When specified, a `space-<label>` entity is added to the `*_electrodes.tsv` filename "
            "and a `*_space-<label>_coordsystem.json` sidecar file is created."
        ),
    )
    archive_target: typing.Literal["dandi", "ember"] | None = None
    use_session_labels: bool = pydantic.Field(
        default=False,
        description=(
            "When True, `ses-` labels and session-level subdirectories are always included in BIDS output, "
            "even when every subject has only a single session."
        ),
    )
    probe: str | None = pydantic.Field(
        default=None,
        description=(
            "When set, fetches the ProbeInterface JSON for the specified probe from the ProbeInterface library "
            "and writes it to the ``probes/`` directory of the BIDS dataset. "
            "The value must follow the ``manufacturer/model`` format used by the ProbeInterface library, "
            "e.g. ``neuronexus/A1x32-Poly3-10mm-50-177``."
        ),
    )
    silent: bool = False
    _nwb2bids_directory: pathlib.Path = pydantic.PrivateAttr()

    model_config = pydantic.ConfigDict(
        frozen=True,  # Make the model immutable
        validate_default=True,  # Validate default values as well
    )

    def model_post_init(self, context: typing.Any, /) -> None:
        self._nwb2bids_directory = self.bids_directory / ".nwb2bids"

    @pydantic.computed_field
    @property
    def sanitization_file_path(self) -> pathlib.Path:
        """The file path leading to a record of sanitizations made."""
        sanitization_file_path = self._nwb2bids_directory / f"{self.run_id}_sanitization.txt"
        return sanitization_file_path

    @pydantic.computed_field
    @property
    def notifications_file_path(self) -> pathlib.Path:
        """The file path leading to a human-readable notifications report."""
        notifications_file_path = self._nwb2bids_directory / f"{self.run_id}_notifications.txt"
        return notifications_file_path

    @pydantic.computed_field
    @property
    def notifications_json_file_path(self) -> pathlib.Path:
        """The file path leading to a JSON dump of the notifications."""
        notifications_file_path = self._nwb2bids_directory / f"{self.run_id}_notifications.json"
        return notifications_file_path

    @classmethod
    def from_dotenv_files(cls, **explicit_kwargs: typing.Any) -> "RunConfig":
        """
        Create a :class:`RunConfig` with defaults loaded from ``.env`` configuration files.

        Reads persistent defaults from:

        * ``~/.nwb2bids/.env`` — global (user-level) configuration
        * ``<bids_directory>/.nwb2bids/.env`` — local (dataset-specific) configuration

        Environment variables prefixed with ``NWB2BIDS_`` override values read from the files.
        Any keyword arguments passed directly to this method override everything else.

        Priority order (lowest → highest):

        1. ``~/.nwb2bids/.env``
        2. ``<bids_directory>/.nwb2bids/.env``
        3. ``NWB2BIDS_*`` environment variables
        4. *explicit_kwargs* (highest priority)

        Parameters
        ----------
        **explicit_kwargs :
            Keyword arguments forwarded directly to :class:`RunConfig`.
            These take precedence over any value from a config file or environment variable.

        Examples
        --------
        Given ``~/.nwb2bids/.env`` containing::

            NWB2BIDS_FILE_MODE=symlink
            NWB2BIDS_SANITIZATION_SUB_LABELS=true

        >>> run_config = RunConfig.from_dotenv_files(bids_directory="/tmp/my_bids")
        >>> run_config.file_mode  # from global config file
        'symlink'

        An explicitly provided keyword argument still wins::

        >>> run_config = RunConfig.from_dotenv_files(bids_directory="/tmp/my_bids", file_mode="copy")
        >>> run_config.file_mode  # explicit kwarg overrides .env value
        'copy'
        """
        bids_directory = explicit_kwargs.get("bids_directory")
        bids_directory_path = pathlib.Path(bids_directory) if bids_directory is not None else None
        dotenv_defaults = _load_run_config_defaults(bids_directory=bids_directory_path)

        # Explicit kwargs win over dotenv defaults
        merged = {**dotenv_defaults, **explicit_kwargs}
        return cls(**merged)

    @pydantic.field_validator("bids_directory", mode="after")
    @classmethod
    def validate_bids_directory(cls, value: pathlib.Path) -> pathlib.Path:
        return _validate_bids_directory(value)
