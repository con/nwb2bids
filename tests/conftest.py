import json
import pathlib

import numpy
import py.path
import pynwb
import pynwb.file
import pynwb.testing.mock.file
import pytest

import nwb2bids

# TODO: add ndx-events
# TODO: add DynamicTable's in acquisition with *_time columns


@pytest.fixture()
def temporary_bids_directory(tmpdir: py.path.local) -> pathlib.Path:
    """Creates a temporary BIDS directory for testing purposes."""
    return pathlib.Path(tmpdir)


@pytest.fixture(scope="session")
def nwb_file_with_multiple_events(
    tmp_path_factory: pytest.TempPathFactory,
) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="20240309")
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.testing.mock.file.mock_Subject()
    nwbfile.subject = subject

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    epochs = nwb2bids.testing.mock_epochs_table()
    nwbfile.epochs = epochs

    time_intervals = nwb2bids.testing.mock_time_intervals()
    nwbfile.add_acquisition(time_intervals)

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_multiple_events.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_file_with_trials_events(
    tmp_path_factory: pytest.TempPathFactory,
) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="20240309")
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.file.Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_trials.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_file_with_epochs_events(
    tmp_path_factory: pytest.TempPathFactory,
) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="20240309")
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.file.Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject

    epochs = nwb2bids.testing.mock_epochs_table()
    nwbfile.epochs = epochs

    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_epochs.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_file(
    tmp_path_factory: pytest.TempPathFactory,
) -> pathlib.Path:

    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="20240309")
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.file.Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject
    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def nwb_file_with_missing_session_id(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile()
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.file.Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject
    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_nosessionid.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename


@pytest.fixture(scope="session")
def additional_metadata_file_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> pathlib.Path:
    additional_metadata_dictionary = {
        "dataset_description": {
            "Name": "test",
            "Description": "TODO",
            "BIDSVersion": "1.10",
            "DatasetType": "raw",
            "License": "CC-BY-4.0",
            "Authors": ["Cody Baker", "Yaroslav Halchenko"],
        }
    }

    file_path = tmp_path_factory.mktemp("test_nwb2bids") / "test_additional_metadata.json"
    with file_path.open(mode="w") as file_stream:
        json.dump(obj=additional_metadata_dictionary, fp=file_stream)

    return file_path
