import pynwb
import pynwb.testing.mock.base


def mock_trials_table(nwbfile: pynwb.NWBFile | None = None) -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock trials table.

    These are shorter than epochs and fit neatly within them in a qualitative manner.
    If a NWBFile is provided, a TimeSeriesReference to a mock TimeSeries will be added to each trial.
    """
    trials = pynwb.epoch.TimeIntervals(name="trials", description="A mock trials table.")
    trials.add_column(name="trial_condition", description="Extra information per trial.")
    trials.add_column(
        name="indexed_column",
        description="A more complicated type of column that contains structured data.",
        index=True,
    )

    kwargs_per_row = [
        {"start_time": 0.0, "stop_time": 1.0, "trial_condition": "A", "indexed_column": [0, 1]},
        {"start_time": 2.0, "stop_time": 3.0, "trial_condition": "B", "indexed_column": [2, 3]},
        {"start_time": 5.0, "stop_time": 5.5, "trial_condition": "C", "indexed_column": [4, 5]},
        {"start_time": 5.5, "stop_time": 6.0, "trial_condition": "D", "indexed_column": [6, 7]},
    ]
    if nwbfile is not None:
        timeseries = pynwb.testing.mock.base.mock_TimeSeries(nwbfile=nwbfile)
        timeseries_ref = pynwb.base.TimeSeriesReference(
            idx_start=0, count=timeseries.data.shape[0], timeseries=timeseries
        )

        for kwargs in kwargs_per_row:
            kwargs["timeseries"] = [timeseries_ref]
    for kwargs in kwargs_per_row:
        trials.add_row(**kwargs)

    return trials


def mock_epochs_table() -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock epochs table.

    These are longer than trials and encompass several of them in a qualitative manner.
    """
    epochs = pynwb.epoch.TimeIntervals(name="epochs", description="A mock epochs table.")
    epochs.add_column(name="epoch_condition", description="Extra information per epoch.")
    epochs.add_row(start_time=0.0, stop_time=3.5, epoch_condition="AB")
    epochs.add_row(start_time=4.5, stop_time=6.0, epoch_condition="CD")

    return epochs


def mock_time_intervals() -> pynwb.epoch.TimeIntervals:
    """Generate a mock time intervals table."""
    time_intervals = pynwb.epoch.TimeIntervals(name="mock_time_intervals", description="A mock time intervals table.")
    time_intervals.add_column(name="tag", description="A tag assigned to each interval.")
    time_intervals.add_row(start_time=0.5, stop_time=0.75, tag="tag1")
    time_intervals.add_row(start_time=5.1, stop_time=5.23, tag="tag2")

    return time_intervals


def mock_events_table() -> "ndx_events.EventsTable":  # type: ignore[name-defined]
    """
    Generate a mock ndx-events ``EventsTable`` with timestamps only (no duration).

    Durations will appear as ``n/a`` in the BIDS TSV output.
    """
    import ndx_events

    timestamp = ndx_events.TimestampVectorData(
        name="timestamp",
        description="Timestamps of the mock events.",
        data=[0.5, 1.0, 2.5, 3.0],
    )
    return ndx_events.EventsTable(
        name="mock_events",
        description="A mock ndx-events EventsTable without duration.",
        columns=[timestamp],
    )


def mock_events_table_with_duration() -> "ndx_events.EventsTable":  # type: ignore[name-defined]
    """
    Generate a mock ndx-events ``EventsTable`` with both timestamps and durations.

    The last event has a ``NaN`` duration to exercise the ``n/a`` path in the BIDS TSV output.
    """
    import ndx_events

    timestamp = ndx_events.TimestampVectorData(
        name="timestamp",
        description="Timestamps of the mock events.",
        data=[0.5, 1.0, 2.5, 3.0],
    )
    duration = ndx_events.DurationVectorData(
        name="duration",
        description="Durations of the mock events.",
        data=[0.25, 0.5, float("nan"), 0.1],
    )
    return ndx_events.EventsTable(
        name="mock_events_with_duration",
        description="A mock ndx-events EventsTable with duration.",
        columns=[timestamp, duration],
    )


def mock_events_table_with_label() -> "ndx_events.EventsTable":  # type: ignore[name-defined]
    """
    Generate a mock ndx-events ``EventsTable`` with timestamps and a categorical label column.
    """
    import ndx_events
    from hdmf.common import VectorData

    timestamp = ndx_events.TimestampVectorData(
        name="timestamp",
        description="Timestamps of the mock events.",
        data=[0.5, 1.0, 2.5, 3.0],
    )
    label = VectorData(
        name="label",
        description="Categorical label for each event.",
        data=["stim_A", "stim_B", "stim_A", "stim_B"],
    )
    return ndx_events.EventsTable(
        name="mock_events_with_label",
        description="A mock ndx-events EventsTable with a label column.",
        columns=[timestamp, label],
    )
