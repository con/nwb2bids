import json

import pynwb
import numpy
import pytest
from datetime import datetime
from dateutil import tz


def _generate_mock_trials_table() -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock trials table.

    These are shorter than epochs and fit neatly within them in a qualitative manner.
    """
    trials = pynwb.epoch.TimeIntervals(
        name="trials", description="A mock trials table."
    )
    trials.add_column(
        name="trial_condition", description="Extra information per trial."
    )
    trials.add_row(start_time=0.0, stop_time=1.0, trial_condition="A")
    trials.add_row(start_time=2.0, stop_time=3.0, trial_condition="B")
    trials.add_row(start_time=5.0, stop_time=5.5, trial_condition="C")
    trials.add_row(start_time=5.5, stop_time=6.0, trial_condition="D")

    return trials


def _generate_mock_epochs_table() -> pynwb.epoch.TimeIntervals:
    """
    Generate a mock epochs table.

    These are longer than trials and encompass several of them in a qualitative manner.
    """
    epochs = pynwb.epoch.TimeIntervals(
        name="epochs", description="A mock epochs table."
    )
    epochs.add_column(
        name="epoch_condition", description="Extra information per epoch."
    )
    epochs.add_row(start_time=0.0, stop_time=3.5, epoch_condition="AB")
    epochs.add_row(start_time=4.5, stop_time=6.0, epoch_condition="CD")

    return epochs


def _generate_mock_time_intervals() -> pynwb.epoch.TimeIntervals:
    """Generate a mock time intervals table."""
    time_intervals = pynwb.epoch.TimeIntervals(
        name="mock_time_intervals", description="A mock time intervals table."
    )
    time_intervals.add_column(
        name="tag", description="A tag assigned to each interval."
    )
    time_intervals.add_row(start_time=0.5, stop_time=0.75, tag="tag1")
    time_intervals.add_row(start_time=5.1, stop_time=5.23, tag="tag2")

    return time_intervals


# TODO: add ndx-events
# TODO: add DynamicTable's in acquisition with *_time columns


@pytest.fixture(scope="session")
def nwb_testdata_multiple_events(
    tmp_path_factory,
):
    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.file import Subject

    nwbfile = mock_NWBFile(
        session_start_time=datetime(
            2024, 3, 9, 22, 30, 3, tzinfo=tz.gettz("US/Eastern")
        ),
        session_id="20240309",
    )
    time_series = pynwb.TimeSeries(
        name="Test", data=numpy.array([], dtype="uint8"), unit="n.a.", rate=1.0
    )
    nwbfile.add_acquisition(time_series)

    subject = Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject

    trials = _generate_mock_trials_table()
    nwbfile.trials = trials

    epochs = _generate_mock_epochs_table()
    nwbfile.epochs = epochs

    time_intervals = _generate_mock_time_intervals()
    nwbfile.add_acquisition(time_intervals)

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_multiple_events.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_testdata_trials_events(
    tmp_path_factory,
):
    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.file import Subject

    nwbfile = mock_NWBFile(
        session_start_time=datetime(
            2024, 3, 9, 22, 30, 3, tzinfo=tz.gettz("US/Eastern")
        ),
        session_id="20240309",
    )
    time_series = pynwb.TimeSeries(
        name="Test", data=numpy.array([], dtype="uint8"), unit="n.a.", rate=1.0
    )
    nwbfile.add_acquisition(time_series)

    subject = Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject

    trials = _generate_mock_trials_table()
    nwbfile.trials = trials

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_trials.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_testdata_epochs_events(
    tmp_path_factory,
):
    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.file import Subject

    nwbfile = mock_NWBFile(
        session_start_time=datetime(
            2024, 3, 9, 22, 30, 3, tzinfo=tz.gettz("US/Eastern")
        ),
        session_id="20240309",
    )
    time_series = pynwb.TimeSeries(
        name="Test", data=numpy.array([], dtype="uint8"), unit="n.a.", rate=1.0
    )
    nwbfile.add_acquisition(time_series)

    subject = Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject

    epochs = _generate_mock_epochs_table()
    nwbfile.epochs = epochs

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_epochs.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_testdata(
    tmp_path_factory,
):
    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.file import Subject

    nwbfile = mock_NWBFile(
        session_start_time=datetime(
            2024, 3, 9, 22, 30, 3, tzinfo=tz.gettz("US/Eastern")
        ),
        session_id="20240309",
    )
    time_series = pynwb.TimeSeries(
        name="Test", data=numpy.array([], dtype="uint8"), unit="n.a.", rate=1.0
    )
    nwbfile.add_acquisition(time_series)

    subject = Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject
    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_testdata_nosessionid(tmp_path_factory):
    from pynwb.testing.mock.file import mock_NWBFile
    from pynwb.file import Subject

    nwbfile = mock_NWBFile(
        session_start_time=datetime(
            2024, 3, 9, 22, 30, 3, tzinfo=tz.gettz("US/Eastern")
        ),
        session_id="",
    )
    time_series = pynwb.TimeSeries(
        name="Test", data=numpy.array([], dtype="uint8"), unit="n.a.", rate=1.0
    )
    nwbfile.add_acquisition(time_series)

    subject = Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject
    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_nosessionid.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def additional_metadata_fixture(
    tmp_path_factory,
):
    additional_metdata_dictionary = {
        "dataset_description": {
            "Name": "test",
            "Description": "TODO",
            "BIDSVersion": "1.10",
            "DatasetType": "raw",
            "License": "CC-BY-4.0",
            "Authors": ["Cody Baker", "Yaroslav Halchenko"],
        }
    }

    file_path = (
        tmp_path_factory.mktemp("test_nwb2bids") / "test_additional_metadata.json"
    )
    with file_path.open(mode="w") as file_stream:
        json.dump(obj=additional_metdata_dictionary, fp=file_stream)

    return file_path
