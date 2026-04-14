"""Integration tests for the `convert_nwb_dataset` function with ndx-events data types."""

import json
import pathlib

import pandas
import pytest

import nwb2bids

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_COMMON_EXPECTED_STRUCTURE_ECEPHYS = {
    "directories": set(),
    "files": {
        "sub-123_ses-456_ecephys.nwb",
        "sub-123_ses-456_events.tsv",
        "sub-123_ses-456_events.json",
    },
}


def _ecephys_path(bids_dir: pathlib.Path) -> pathlib.Path:
    return bids_dir / "sub-123" / "ses-456" / "ecephys"


def _run_conversion(
    nwbfile_path: pathlib.Path, bids_dir: pathlib.Path
) -> nwb2bids.DatasetConverter:  # type: ignore[name-defined]
    run_config = nwb2bids.RunConfig(bids_directory=bids_dir)
    return nwb2bids.convert_nwb_dataset(nwb_paths=[nwbfile_path], run_config=run_config)


# ---------------------------------------------------------------------------
# EventsTable – timestamps only (no duration)
# ---------------------------------------------------------------------------


def test_ndx_events_table_tsv(ndx_events_table_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    """EventsTable with timestamps only should have 'n/a' in the duration column."""
    dataset_converter = _run_conversion(ndx_events_table_nwbfile_path, temporary_bids_directory)
    assert not any(dataset_converter.notifications)

    tsv_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.tsv"
    df = pandas.read_csv(filepath_or_buffer=tsv_path, sep="\t")

    assert list(df.columns[:3]) == ["onset", "duration", "nwb_table"]
    assert df["nwb_table"].unique().tolist() == ["mock_events"]
    # All durations should be n/a (no DurationVectorData was provided)
    assert df["duration"].isna().all()
    # Onset values match the mock data
    assert df["onset"].tolist() == [0.5, 1.0, 2.5, 3.0]


def test_ndx_events_table_json(ndx_events_table_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    """EventsTable JSON sidecar should describe onset, duration, nwb_table, and the table itself."""
    _run_conversion(ndx_events_table_nwbfile_path, temporary_bids_directory)

    json_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.json"
    with json_path.open() as f:
        metadata = json.load(f)

    assert "onset" in metadata
    assert "duration" in metadata
    assert "nwb_table" in metadata
    assert "mock_events" in metadata["nwb_table"]["Levels"]
    assert "mock_events" in metadata["nwb_table"]["HED"]
    assert metadata["nwb_table"]["HED"]["mock_events"] == "Sensory-event"
    assert "mock_events" in metadata
    assert metadata["mock_events"]["Description"] == "A mock ndx-events EventsTable without duration."


# ---------------------------------------------------------------------------
# EventsTable – with duration (some NaN)
# ---------------------------------------------------------------------------


def test_ndx_events_table_with_duration_tsv(
    ndx_events_table_with_duration_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """EventsTable with a DurationVectorData should use real values and 'n/a' for NaN."""
    _run_conversion(ndx_events_table_with_duration_nwbfile_path, temporary_bids_directory)

    tsv_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.tsv"
    df = pandas.read_csv(filepath_or_buffer=tsv_path, sep="\t")

    assert list(df.columns[:3]) == ["onset", "duration", "nwb_table"]
    assert df["nwb_table"].unique().tolist() == ["mock_events_with_duration"]

    # Rows sorted by onset, NaN duration last within the same onset
    assert df["onset"].tolist() == [0.5, 1.0, 2.5, 3.0]
    # duration values: 0.25, 0.5, n/a (NaN), 0.1
    assert df["duration"].tolist()[0] == pytest.approx(0.25)
    assert df["duration"].tolist()[1] == pytest.approx(0.5)
    assert pandas.isna(df["duration"].tolist()[2])
    assert df["duration"].tolist()[3] == pytest.approx(0.1)


def test_ndx_events_table_with_duration_json(
    ndx_events_table_with_duration_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """EventsTable with duration should include table description in JSON sidecar."""
    _run_conversion(ndx_events_table_with_duration_nwbfile_path, temporary_bids_directory)

    json_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.json"
    with json_path.open() as f:
        metadata = json.load(f)

    assert "mock_events_with_duration" in metadata
    assert metadata["mock_events_with_duration"]["Description"] == "A mock ndx-events EventsTable with duration."


# ---------------------------------------------------------------------------
# EventsTable – with a label column
# ---------------------------------------------------------------------------


def test_ndx_events_table_with_label_tsv(
    ndx_events_table_with_label_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """EventsTable with a label column should preserve that column in the TSV."""
    _run_conversion(ndx_events_table_with_label_nwbfile_path, temporary_bids_directory)

    tsv_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.tsv"
    df = pandas.read_csv(filepath_or_buffer=tsv_path, sep="\t")

    assert "label" in df.columns
    assert df["label"].tolist() == ["stim_A", "stim_B", "stim_A", "stim_B"]
    assert df["duration"].isna().all()


def test_ndx_events_table_with_label_json(
    ndx_events_table_with_label_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    """EventsTable with a label column should include the column description in the JSON sidecar."""
    _run_conversion(ndx_events_table_with_label_nwbfile_path, temporary_bids_directory)

    json_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.json"
    with json_path.open() as f:
        metadata = json.load(f)

    assert "label" in metadata
    assert metadata["label"]["Description"] == "Categorical label for each event."


# ---------------------------------------------------------------------------
# Mixed: ndx-events EventsTable + TimeIntervals in the same file
# ---------------------------------------------------------------------------


def test_ndx_events_mixed_with_time_intervals_tsv(
    ndx_events_mixed_with_time_intervals_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    """
    When an NWB file contains both a TimeIntervals table and an ndx-events EventsTable, both
    sources should be represented in the output TSV with proper nwb_table labels.
    """
    _run_conversion(ndx_events_mixed_with_time_intervals_nwbfile_path, temporary_bids_directory)

    tsv_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.tsv"
    df = pandas.read_csv(filepath_or_buffer=tsv_path, sep="\t")

    # Both tables should be present
    assert set(df["nwb_table"].unique()) == {"trials", "mock_events"}

    # TimeIntervals rows should have numeric durations
    trials_rows = df[df["nwb_table"] == "trials"]
    assert trials_rows["duration"].dtype != object  # not strings

    # ndx-events rows should have n/a (NaN) durations
    events_rows = df[df["nwb_table"] == "mock_events"]
    assert events_rows["duration"].isna().all()


def test_ndx_events_mixed_with_time_intervals_json(
    ndx_events_mixed_with_time_intervals_nwbfile_path: pathlib.Path,
    temporary_bids_directory: pathlib.Path,
):
    """JSON sidecar should include entries for both source tables when sources are mixed."""
    _run_conversion(ndx_events_mixed_with_time_intervals_nwbfile_path, temporary_bids_directory)

    json_path = _ecephys_path(temporary_bids_directory) / "sub-123_ses-456_events.json"
    with json_path.open() as f:
        metadata = json.load(f)

    levels = metadata["nwb_table"]["Levels"]
    hed = metadata["nwb_table"]["HED"]

    # TimeIntervals entry uses Time-interval HED tag (or Experimental-trial for "trials")
    assert "trials" in levels
    assert hed["trials"] == "Experimental-trial"

    # ndx-events entry uses Sensory-event HED tag
    assert "mock_events" in levels
    assert hed["mock_events"] == "Sensory-event"
