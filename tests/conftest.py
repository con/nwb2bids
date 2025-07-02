import json
import pathlib

import py.path
import pynwb
import pynwb.file
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file
import pytest

import nwb2bids

# TODO: add ndx-events
# TODO: add DynamicTable's in acquisition with *_time columns


def _make_minimal_nwbfile() -> pynwb.NWBFile:
    """Creates a minimal NWB file for testing purposes."""
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="456")

    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="male",
    )
    nwbfile.subject = subject

    return nwbfile


@pytest.fixture()
def temporary_bids_directory(tmpdir: py.path.local) -> pathlib.Path:
    """Creates a temporary BIDS directory for testing purposes."""
    return pathlib.Path(tmpdir)


@pytest.fixture(scope="session")
def testing_files_directory(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """
    Creates a common temporary directory for all testing files.

    Testing files may be nested into subdirectories to test localization logic.
    """
    testing_files_directory = tmp_path_factory.mktemp(basename="nwb2bids_testing_files", numbered=False)
    return testing_files_directory


@pytest.fixture(scope="session")
def additional_metadata_file_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
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

    additional_metadata_subdirectory = testing_files_directory / "additional_metadata"
    additional_metadata_subdirectory.mkdir(exist_ok=True)
    file_path = additional_metadata_subdirectory / "test_additional_metadata.json"
    with file_path.open(mode="w") as file_stream:
        json.dump(obj=additional_metadata_dictionary, fp=file_stream)

    return file_path


@pytest.fixture(scope="session")
def minimal_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A minimally valid NWB file for testing purposes.

    Does not contain any additional metadata beyond what is required for initialization of converter and metadata
    classes.
    """
    nwbfile = _make_minimal_nwbfile()

    minimal_subdirectory = testing_files_directory / "minimal"
    minimal_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = minimal_subdirectory / "minimal.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ecephys_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = _make_minimal_nwbfile()

    pynwb.testing.mock.ecephys.mock_ElectricalSeries(name="test_electrical_series", nwbfile=nwbfile)

    ecephys_subdirectory = testing_files_directory / "ecephys"
    ecephys_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ecephys_subdirectory / "ecephys.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def trials_events_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = _make_minimal_nwbfile()

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    events_subdirectory = testing_files_directory / "trials"
    events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = events_subdirectory / "trials.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def epochs_events_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = _make_minimal_nwbfile()

    epochs = nwb2bids.testing.mock_epochs_table()
    nwbfile.epochs = epochs

    events_subdirectory = testing_files_directory / "epochs"
    events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = events_subdirectory / "epochs.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def multiple_events_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = _make_minimal_nwbfile()

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    epochs = nwb2bids.testing.mock_epochs_table()
    nwbfile.epochs = epochs

    time_intervals = nwb2bids.testing.mock_time_intervals()
    nwbfile.add_acquisition(time_intervals)

    events_subdirectory = testing_files_directory / "multiple_events"
    events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = events_subdirectory / "multiple_events.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def nwbfile_path_with_missing_session_id(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id=None)

    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    events_subdirectory = testing_files_directory / "missing_session_id"
    events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = events_subdirectory / "missing_session_id.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path
