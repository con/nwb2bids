"""
Utilities for loading persistent global configuration for nwb2bids.

Configuration is loaded from ``.env`` files at two levels, with the following priority order
(highest to lowest):

1. Manually passed flags to the CLI or Python API
2. Environment variables with the ``NWB2BIDS_`` prefix
3. Local (dataset-specific) configuration: ``.nwb2bids/.env`` in the dataset directory
4. Global (user-specific) configuration: ``~/.nwb2bids/.env``
5. Model defaults

The ``.env`` files use the standard dotenv format.  Each line should contain an entry of the form
``KEY=value``, where the key is a ``NWB2BIDS_``-prefixed environment variable name.

Example ``.env`` file::

    NWB2BIDS_FILE_MODE=symlink
    NWB2BIDS_ARCHIVE_TARGET=dandi
    NWB2BIDS_SANITIZATION_SUB_LABELS=true
    NWB2BIDS_SANITIZATION_SES_LABELS=false
"""

import os
import pathlib
import typing

import dotenv

_ENV_VAR_PREFIX = "NWB2BIDS_"

# Map from environment variable name to the corresponding RunConfig field name.
# Fields whose values remain plain strings (no extra coercion needed).
_FIELD_ENV_VARS: dict[str, str] = {
    "NWB2BIDS_FILE_MODE": "file_mode",
    "NWB2BIDS_CACHE_DIRECTORY": "cache_directory",
    "NWB2BIDS_ARCHIVE_TARGET": "archive_target",
    "NWB2BIDS_SPACE": "space",
}

# Map from environment variable name to the SanitizationConfig field name.
# These require boolean coercion and are assembled into a nested SanitizationConfig object.
_SANITIZATION_ENV_VARS: dict[str, str] = {
    "NWB2BIDS_SANITIZATION_SUB_LABELS": "sub_labels",
    "NWB2BIDS_SANITIZATION_SES_LABELS": "ses_labels",
}


def _get_global_config_file_path() -> pathlib.Path:
    """
    Return the path to the global (user-level) configuration file.

    The global config file lives at ``~/.nwb2bids/.env``.
    """
    return pathlib.Path.home() / ".nwb2bids" / ".env"


def _get_local_config_file_path(directory: pathlib.Path | None = None) -> pathlib.Path:
    """
    Return the path to the local (dataset-specific) configuration file.

    The local config file lives at ``<directory>/.nwb2bids/.env``.
    If *directory* is ``None``, the current working directory is used.

    Parameters
    ----------
    directory :
        The directory to look for the local config file.
    """
    if directory is None:
        directory = pathlib.Path.cwd()
    return directory / ".nwb2bids" / ".env"


def _parse_bool(value: str) -> bool:
    """Coerce a dotenv string value to a Python :class:`bool`.

    Accepted truthy strings (case-insensitive): ``"true"``, ``"1"``, ``"yes"``, ``"on"``.
    All other values are treated as ``False``.
    """
    return value.strip().lower() in ("true", "1", "yes", "on")


def _load_run_config_defaults(
    bids_directory: pathlib.Path | None = None,
) -> dict[str, typing.Any]:
    """
    Resolve ``RunConfig`` defaults from ``.env`` files and environment variables.

    Reads the global and (optionally) local ``.env`` config files, then applies any matching
    environment variables on top.  The resulting dict can be used as keyword arguments to
    :class:`~nwb2bids.RunConfig`, with explicit caller-supplied kwargs taking precedence.

    Priority order (lowest → highest):

    1. ``~/.nwb2bids/.env`` (global config)
    2. ``<bids_directory>/.nwb2bids/.env`` (local config, overrides global)
    3. ``NWB2BIDS_*`` environment variables (override file values)

    Parameters
    ----------
    bids_directory :
        The dataset directory used to locate the local ``.nwb2bids/.env`` file.
        Falls back to the current working directory when ``None``.

    Returns
    -------
    dict
        Keyword arguments suitable for :class:`~nwb2bids.RunConfig`.
    """
    raw: dict[str, str] = {}

    # 1. Global config file
    global_path = _get_global_config_file_path()
    if global_path.exists():
        raw.update({k: v for k, v in dotenv.dotenv_values(global_path).items() if v is not None})

    # 2. Local config file (overrides global)
    local_path = _get_local_config_file_path(bids_directory)
    if local_path.exists():
        raw.update({k: v for k, v in dotenv.dotenv_values(local_path).items() if v is not None})

    # 3. Environment variables override file values.
    #    First update keys already discovered from files…
    for key in list(raw.keys()):
        env_value = os.environ.get(key)
        if env_value is not None:
            raw[key] = env_value
    #    …then pick up any additional NWB2BIDS_* env vars not present in any file.
    for env_key, env_value in os.environ.items():
        if env_key.startswith(_ENV_VAR_PREFIX) and env_key not in raw:
            raw[env_key] = env_value

    return _parse_raw_config(raw)


def _parse_raw_config(raw: dict[str, str]) -> dict[str, typing.Any]:
    """
    Convert raw string env-var key/value pairs into typed :class:`~nwb2bids.RunConfig` kwargs.

    Parameters
    ----------
    raw :
        A mapping of ``NWB2BIDS_*`` env var names to their string values.

    Returns
    -------
    dict
        Typed keyword arguments suitable for :class:`~nwb2bids.RunConfig`.
    """
    # Deferred import to avoid a circular dependency:
    # _global_config -> sanitization -> (potentially) _run_config -> _global_config.
    from ..sanitization import SanitizationConfig

    result: dict[str, typing.Any] = {}
    sanitization_kwargs: dict[str, bool] = {}

    for env_var, field_name in _FIELD_ENV_VARS.items():
        value = raw.get(env_var)
        if value is not None:
            result[field_name] = value

    for env_var, sanitization_field in _SANITIZATION_ENV_VARS.items():
        value = raw.get(env_var)
        if value is not None:
            sanitization_kwargs[sanitization_field] = _parse_bool(value)

    if sanitization_kwargs:
        result["sanitization_config"] = SanitizationConfig(**sanitization_kwargs)

    return result
