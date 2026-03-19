"""Tests for the persistent global configuration loading mechanism."""

import pathlib

import pytest

import nwb2bids
from nwb2bids._core._global_config import (
    _get_global_config_file_path,
    _get_local_config_file_path,
    _load_run_config_defaults,
    _parse_bool,
    _parse_raw_config,
)
from nwb2bids.sanitization import SanitizationConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_dotenv(path: pathlib.Path, contents: str) -> None:
    """Write *contents* to *path*, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)


# ---------------------------------------------------------------------------
# Unit tests for _parse_bool
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"])
def test_parse_bool_truthy(value: str) -> None:
    assert _parse_bool(value) is True


@pytest.mark.parametrize("value", ["  true  ", "  1  ", "  yes  ", "  on  "])
def test_parse_bool_truthy_with_whitespace(value: str) -> None:
    assert _parse_bool(value) is True


@pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF", "anything"])
def test_parse_bool_falsy(value: str) -> None:
    assert _parse_bool(value) is False


# ---------------------------------------------------------------------------
# Unit tests for _parse_raw_config
# ---------------------------------------------------------------------------


def test_parse_raw_config_empty() -> None:
    assert _parse_raw_config({}) == {}


def test_parse_raw_config_file_mode() -> None:
    result = _parse_raw_config({"NWB2BIDS_FILE_MODE": "copy"})
    assert result == {"file_mode": "copy"}


def test_parse_raw_config_sanitization() -> None:
    result = _parse_raw_config(
        {
            "NWB2BIDS_SANITIZATION_SUB_LABELS": "true",
            "NWB2BIDS_SANITIZATION_SES_LABELS": "false",
        }
    )
    assert "sanitization_config" in result
    assert isinstance(result["sanitization_config"], SanitizationConfig)
    assert result["sanitization_config"].sub_labels is True
    assert result["sanitization_config"].ses_labels is False


def test_parse_raw_config_mixed() -> None:
    result = _parse_raw_config(
        {
            "NWB2BIDS_FILE_MODE": "move",
            "NWB2BIDS_ARCHIVE_TARGET": "dandi",
            "NWB2BIDS_SANITIZATION_SES_LABELS": "true",
        }
    )
    assert result["file_mode"] == "move"
    assert result["archive_target"] == "dandi"
    assert result["sanitization_config"].ses_labels is True


def test_parse_raw_config_ignores_unknown_keys() -> None:
    result = _parse_raw_config({"NWB2BIDS_UNKNOWN_KEY": "value"})
    assert result == {}


# ---------------------------------------------------------------------------
# Config file path helpers
# ---------------------------------------------------------------------------


def test_get_global_config_file_path() -> None:
    expected = pathlib.Path.home() / ".nwb2bids" / ".env"
    assert _get_global_config_file_path() == expected


def test_get_local_config_file_path_default() -> None:
    expected = pathlib.Path.cwd() / ".nwb2bids" / ".env"
    assert _get_local_config_file_path() == expected


def test_get_local_config_file_path_custom(tmp_path: pathlib.Path) -> None:
    assert _get_local_config_file_path(tmp_path) == tmp_path / ".nwb2bids" / ".env"


# ---------------------------------------------------------------------------
# Integration tests for _load_run_config_defaults
# ---------------------------------------------------------------------------


def test_load_run_config_defaults_no_files(tmp_path: pathlib.Path) -> None:
    """Returns empty dict when no config files exist and no env vars are set."""
    result = _load_run_config_defaults(bids_directory=tmp_path)
    assert result == {}


def test_load_run_config_defaults_from_global_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Values from the global config file are returned as defaults."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    global_env = fake_home / ".nwb2bids" / ".env"
    _write_dotenv(global_env, "NWB2BIDS_FILE_MODE=copy\n")

    result = _load_run_config_defaults(bids_directory=tmp_path)
    assert result.get("file_mode") == "copy"


def test_load_run_config_defaults_local_overrides_global(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Local config file values override global config file values."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_FILE_MODE=copy\n")
    _write_dotenv(bids_dir / ".nwb2bids" / ".env", "NWB2BIDS_FILE_MODE=move\n")

    result = _load_run_config_defaults(bids_directory=bids_dir)
    assert result["file_mode"] == "move"


def test_load_run_config_defaults_env_var_overrides_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Environment variables take precedence over config file values."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_FILE_MODE=copy\n")
    monkeypatch.setenv("NWB2BIDS_FILE_MODE", "symlink")

    result = _load_run_config_defaults(bids_directory=tmp_path)
    assert result["file_mode"] == "symlink"


def test_load_run_config_defaults_env_var_without_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """NWB2BIDS_* env vars are picked up even when no config files exist."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))
    monkeypatch.setenv("NWB2BIDS_ARCHIVE_TARGET", "ember")

    result = _load_run_config_defaults(bids_directory=tmp_path)
    assert result.get("archive_target") == "ember"


def test_load_run_config_defaults_sanitization_from_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sanitization flags from a config file are parsed into a SanitizationConfig."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    _write_dotenv(
        fake_home / ".nwb2bids" / ".env",
        "NWB2BIDS_SANITIZATION_SUB_LABELS=true\n",
    )

    result = _load_run_config_defaults(bids_directory=tmp_path)
    assert isinstance(result.get("sanitization_config"), SanitizationConfig)
    assert result["sanitization_config"].sub_labels is True
    assert result["sanitization_config"].ses_labels is False


# ---------------------------------------------------------------------------
# RunConfig.from_dotenv_files integration
# ---------------------------------------------------------------------------


def test_run_config_from_dotenv_files_uses_global_defaults(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RunConfig.from_dotenv_files picks up values from the global .env file."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_ARCHIVE_TARGET=dandi\n")

    run_config = nwb2bids.RunConfig.from_dotenv_files(bids_directory=bids_dir)
    assert run_config.archive_target == "dandi"


def test_run_config_from_dotenv_files_explicit_kwarg_wins(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit keyword arguments override .env file values in from_dotenv_files."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_ARCHIVE_TARGET=dandi\n")

    run_config = nwb2bids.RunConfig.from_dotenv_files(bids_directory=bids_dir, archive_target="ember")
    assert run_config.archive_target == "ember"


def test_run_config_from_dotenv_files_env_var_wins_over_file(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """NWB2BIDS_* env vars beat .env file values but lose to explicit kwargs."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_ARCHIVE_TARGET=dandi\n")
    monkeypatch.setenv("NWB2BIDS_ARCHIVE_TARGET", "ember")

    run_config = nwb2bids.RunConfig.from_dotenv_files(bids_directory=bids_dir)
    assert run_config.archive_target == "ember"


def test_run_config_from_dotenv_files_local_config_overrides_global(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Local .env takes precedence over global .env in from_dotenv_files."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    _write_dotenv(fake_home / ".nwb2bids" / ".env", "NWB2BIDS_ARCHIVE_TARGET=dandi\n")
    _write_dotenv(bids_dir / ".nwb2bids" / ".env", "NWB2BIDS_ARCHIVE_TARGET=ember\n")

    run_config = nwb2bids.RunConfig.from_dotenv_files(bids_directory=bids_dir)
    assert run_config.archive_target == "ember"


def test_run_config_from_dotenv_files_no_config(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """from_dotenv_files falls back to RunConfig defaults when no .env files exist."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setattr(pathlib.Path, "home", staticmethod(lambda: fake_home))

    # Patch _get_nwb2bids_home_directory to return existing dir so RunConfig doesn't fail
    import nwb2bids._core._home as home_module

    monkeypatch.setattr(home_module, "_get_nwb2bids_home_directory", lambda: fake_home)

    bids_dir = tmp_path / "bids"
    bids_dir.mkdir()

    run_config = nwb2bids.RunConfig.from_dotenv_files(bids_directory=bids_dir)
    # archive_target has no default in .env, so it should be None (model default)
    assert run_config.archive_target is None
    assert run_config.bids_directory == bids_dir
