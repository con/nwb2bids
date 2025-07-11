import pynwb


def mock_trials_table() -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock trials table.

    These are shorter than epochs and fit neatly within them in a qualitative manner.
    """
    trials = pynwb.epoch.TimeIntervals(name="trials", description="A mock trials table.")
    trials.add_column(name="trial_condition", description="Extra information per trial.")
    trials.add_row(start_time=0.0, stop_time=1.0, trial_condition="A")
    trials.add_row(start_time=2.0, stop_time=3.0, trial_condition="B")
    trials.add_row(start_time=5.0, stop_time=5.5, trial_condition="C")
    trials.add_row(start_time=5.5, stop_time=6.0, trial_condition="D")

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
