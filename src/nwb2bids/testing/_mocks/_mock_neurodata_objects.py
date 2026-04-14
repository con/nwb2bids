import numpy
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


def mock_trials_table_with_numpy_column() -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock trials table with a numpy array-valued column.

    Reproduces the scenario from https://github.com/con/nwb2bids/issues/338,
    where a column stores a fixed-size array per trial (e.g. multi-pulse optogenetics data).
    Without serialization, numpy's ``__str__`` inserts line-breaks into wide arrays, breaking TSV rows.
    """
    trials = pynwb.epoch.TimeIntervals(name="trials", description="A mock trials table.")
    trials.add_column(name="trial_condition", description="Extra information per trial.")
    trials.add_column(name="pulse_times", description="Array of pulse timestamps per trial.")

    trials.add_row(
        start_time=0.0,
        stop_time=1.0,
        trial_condition="A",
        pulse_times=numpy.array([float("nan")] * 20),
    )
    trials.add_row(
        start_time=1.0,
        stop_time=2.0,
        trial_condition="B",
        pulse_times=numpy.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] * 2),
    )

    return trials
