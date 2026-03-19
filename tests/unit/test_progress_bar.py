"""Unit tests for progress bar behavior in DatasetConverter and SessionConverter."""

import io
import pathlib
import subprocess
from collections.abc import Callable
from unittest.mock import patch

import pytest

import nwb2bids


@pytest.fixture
def _capturing_tqdm():
    """Factory that creates a tqdm wrapper capturing output to a StringIO buffer."""

    def make(buffer: io.StringIO):
        def capturing_tqdm(iterable, **kwargs):
            kwargs["file"] = buffer
            from tqdm import tqdm as real_tqdm

            return real_tqdm(iterable, **kwargs)

        return capturing_tqdm

    return make


@pytest.mark.ai_generated
def test_run_config_silent_defaults_to_false(temporary_bids_directory: pathlib.Path) -> None:
    """RunConfig.silent should default to False so progress bars are shown by default."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    assert run_config.silent is False


@pytest.mark.ai_generated
def test_run_config_silent_can_be_set_to_true(temporary_bids_directory: pathlib.Path) -> None:
    """RunConfig.silent=True should be accepted and stored correctly."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)
    assert run_config.silent is True


@pytest.mark.ai_generated
def test_session_converter_scan_nwb_files_progress_bar_enabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """A progress bar should be displayed when silent=False during NWB file scanning (SessionConverter)."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.SessionConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["desc"] == "Scanning NWB files"
    assert kwargs["unit"] == "file"
    assert kwargs["disable"] is False


@pytest.mark.ai_generated
def test_session_converter_scan_nwb_files_progress_bar_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """The progress bar should be disabled when silent=True during NWB file scanning (SessionConverter)."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.SessionConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["disable"] is True


@pytest.mark.ai_generated
def test_scan_nwb_files_progress_bar_enabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """A progress bar should be displayed when silent=False during NWB file scanning (DatasetConverter)."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["desc"] == "Scanning NWB files"
    assert kwargs["unit"] == "file"
    assert kwargs["disable"] is False


@pytest.mark.ai_generated
def test_scan_nwb_files_progress_bar_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """The progress bar should be disabled when silent=True during NWB file scanning (DatasetConverter)."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["disable"] is True


@pytest.mark.ai_generated
def test_extract_metadata_progress_bar_enabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """A progress bar should be displayed when silent=False during metadata extraction."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )

    with patch("nwb2bids._converters._dataset_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        dataset_converter.extract_metadata()

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["desc"] == "Extracting metadata"
    assert kwargs["unit"] == "session"
    assert kwargs["disable"] is False


@pytest.mark.ai_generated
def test_extract_metadata_progress_bar_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """The progress bar should be disabled when silent=True during metadata extraction."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )

    with patch("nwb2bids._converters._dataset_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        dataset_converter.extract_metadata()

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["disable"] is True


@pytest.mark.ai_generated
def test_convert_to_bids_dataset_progress_bar_enabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """A progress bar should be displayed when silent=False during BIDS conversion."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )
    dataset_converter.extract_metadata()

    with patch("nwb2bids._converters._dataset_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        dataset_converter.convert_to_bids_dataset()

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["desc"] == "Converting sessions"
    assert kwargs["unit"] == "session"
    assert kwargs["disable"] is False


@pytest.mark.ai_generated
def test_convert_to_bids_dataset_progress_bar_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """The progress bar should be disabled when silent=True during BIDS conversion."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )
    dataset_converter.extract_metadata()

    with patch("nwb2bids._converters._dataset_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        dataset_converter.convert_to_bids_dataset()

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["disable"] is True


@pytest.mark.ai_generated
def test_progress_bar_output_visible_in_stderr(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    _capturing_tqdm,
) -> None:
    """When silent=False, tqdm should write progress output to stderr."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )

    stderr_buffer = io.StringIO()
    with patch("nwb2bids._converters._dataset_converter.tqdm", side_effect=_capturing_tqdm(stderr_buffer)):
        dataset_converter.extract_metadata()

    assert "Extracting metadata" in stderr_buffer.getvalue()


@pytest.mark.ai_generated
def test_progress_bar_no_output_when_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    _capturing_tqdm,
) -> None:
    """When silent=True, tqdm should produce no output."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )

    stderr_buffer = io.StringIO()
    with patch("nwb2bids._converters._dataset_converter.tqdm", side_effect=_capturing_tqdm(stderr_buffer)):
        dataset_converter.extract_metadata()

    assert stderr_buffer.getvalue() == ""


@pytest.mark.ai_generated
@pytest.mark.container_cli_test
def test_cli_silent_suppresses_progress_bar(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
) -> None:
    """The --silent flag should suppress all output including progress bars."""
    command = f"nwb2bids convert {minimal_nwbfile_path} -o {temporary_bids_directory} --silent"
    result = cli_runner(command)

    assert result.returncode == 0
    assert result.stdout == b""
    assert result.stderr == b""


@pytest.mark.ai_generated
@pytest.mark.container_cli_test
def test_cli_without_silent_shows_progress_bar(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    cli_runner: Callable[[str], subprocess.CompletedProcess],
) -> None:
    """Without --silent, tqdm progress bars should appear in stderr."""
    command = f"nwb2bids convert {minimal_nwbfile_path} -o {temporary_bids_directory}"
    result = cli_runner(command)

    assert result.returncode == 0
    # Progress bar output ("Scanning NWB files", "Extracting metadata", "Converting sessions")
    # is written to stderr by tqdm
    assert b"Scanning NWB files" in result.stderr or b"Extracting metadata" in result.stderr
