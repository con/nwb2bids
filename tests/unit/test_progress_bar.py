"""Unit tests for progress bar behavior in DatasetConverter and SessionConverter."""

import io
import pathlib
import subprocess
from collections.abc import Callable
from unittest.mock import patch

import pytest
from tqdm import tqdm as real_tqdm

import nwb2bids

_EXPECTED_OUTPUT_DIR = pathlib.Path(__file__).parent / "expected_progress_output"


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
def test_initialize_sessions_progress_bar_enabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """A progress bar should be displayed when silent=False during session initialization."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["desc"] == "Initializing sessions"
    assert kwargs["unit"] == "session"
    assert kwargs["disable"] is False


@pytest.mark.ai_generated
def test_initialize_sessions_progress_bar_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
) -> None:
    """The progress bar should be disabled when silent=True during session initialization."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)

    with patch("nwb2bids._converters._session_converter.tqdm") as mock_tqdm:
        mock_tqdm.side_effect = lambda iterable, **kwargs: iterable
        nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    mock_tqdm.assert_called_once()
    _, kwargs = mock_tqdm.call_args
    assert kwargs["disable"] is True


@pytest.mark.ai_generated
def test_initialize_sessions_progress_bar_output_visible_in_stderr(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    """Real tqdm output for session initialization should match the golden file content."""
    expected_content = (_EXPECTED_OUTPUT_DIR / "initialize_sessions.txt").read_text().strip()

    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    buffer = io.StringIO()

    def capturing_tqdm(iterable, **kwargs):
        kwargs["file"] = buffer
        return real_tqdm(iterable, **kwargs)

    with patch("nwb2bids._converters._session_converter.tqdm", side_effect=capturing_tqdm):
        nwb2bids.DatasetConverter.from_nwb_paths(nwb_paths=[minimal_nwbfile_path], run_config=run_config)

    captured_output = buffer.getvalue()
    (tmp_path / "initialize_sessions_stderr.txt").write_text(captured_output)

    assert expected_content in captured_output


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
    tmp_path: pathlib.Path,
) -> None:
    """Real tqdm output should contain the expected description text stored in the adjacent golden file."""
    expected_content = (_EXPECTED_OUTPUT_DIR / "extract_metadata.txt").read_text().strip()

    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )
    buffer = io.StringIO()

    def capturing_tqdm(iterable, **kwargs):
        kwargs["file"] = buffer
        return real_tqdm(iterable, **kwargs)

    with patch("nwb2bids._converters._dataset_converter.tqdm", side_effect=capturing_tqdm):
        dataset_converter.extract_metadata()

    captured_output = buffer.getvalue()
    (tmp_path / "extract_metadata_stderr.txt").write_text(captured_output)

    assert expected_content in captured_output


@pytest.mark.ai_generated
def test_progress_bar_no_output_when_disabled(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    """When silent=True, tqdm should produce no output; captured file should be empty."""
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=True)
    dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
        nwb_paths=[minimal_nwbfile_path], run_config=run_config
    )
    buffer = io.StringIO()

    def capturing_tqdm(iterable, **kwargs):
        kwargs["file"] = buffer
        return real_tqdm(iterable, **kwargs)

    with patch("nwb2bids._converters._dataset_converter.tqdm", side_effect=capturing_tqdm):
        dataset_converter.extract_metadata()

    captured_output = buffer.getvalue()
    output_file = tmp_path / "silent_stderr.txt"
    output_file.write_text(captured_output)

    assert captured_output == output_file.read_text() == ""


@pytest.mark.ai_generated
def test_full_workflow_progress_bar_output(
    minimal_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
    tmp_path: pathlib.Path,
) -> None:
    """All three progress bars should appear in succession during a full from_nwb_paths.

    This test also validates that each bar occupies position=0 (the default) and overwrites the previous line in the
    terminal, since we have not set position or leave kwargs.  Because all three bars share the same output buffer
    here, their descriptions appear one after another in captured text, which lets us assert on ordering without
    needing a real TTY.
    """
    expected_lines = (_EXPECTED_OUTPUT_DIR / "full_workflow.txt").read_text().strip().splitlines()

    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory, silent=False)
    buffer = io.StringIO()

    def capturing_tqdm(iterable, **kwargs):
        kwargs["file"] = buffer
        return real_tqdm(iterable, **kwargs)

    with (
        patch("nwb2bids._converters._session_converter.tqdm", side_effect=capturing_tqdm),
        patch("nwb2bids._converters._dataset_converter.tqdm", side_effect=capturing_tqdm),
    ):
        dataset_converter = nwb2bids.DatasetConverter.from_nwb_paths(
            nwb_paths=[minimal_nwbfile_path], run_config=run_config
        )
        dataset_converter.extract_metadata()
        dataset_converter.convert_to_bids_dataset()

    captured_output = buffer.getvalue()
    (tmp_path / "full_workflow_stderr.txt").write_text(captured_output)

    # Verify every expected line appears in the captured output
    for expected_line in expected_lines:
        assert expected_line in captured_output, (
            f"Expected progress bar line {expected_line!r} not found in captured output"
        )

    # Verify the bars appear in the correct order
    positions = [captured_output.index(line) for line in expected_lines]
    assert positions == sorted(positions), "Progress bars did not appear in the expected order"


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
    # Progress bar output ("Extracting metadata", "Converting sessions")
    # is written to stderr by tqdm
    assert b"Extracting metadata" in result.stderr or b"Converting sessions" in result.stderr
