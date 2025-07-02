import json
import pathlib

import numpy
import py.path
import pynwb
import pynwb.file
import pynwb.testing.mock.ecephys
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
def minimal_nwbfile() -> pynwb.NWBFile:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="456")

    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="male",
    )
    nwbfile.subject = subject

    return nwbfile


@pytest.fixture(scope="session")
def minimal_nwbfile_path(testing_files_directory: pathlib.Path, minimal_nwbfile: pynwb.NWBFile) -> pathlib.Path:
    """
    A minimally valid NWB file for testing purposes.

    Does not contain any additional metadata beyond what is required for initialization of converter and metadata
    classes.
    """
    minimal_subdirectory = testing_files_directory / "minimal"
    minimal_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = minimal_subdirectory / "minimal.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(minimal_nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ecephys_nwbfile() -> pynwb.NWBFile:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="456")

    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="male",
    )
    nwbfile.subject = subject

    device = pynwb.testing.mock.ecephys.mock_Device(name="test_device", description="A test device.", nwbfile=nwbfile)
    electrode_group = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(
        name="test_electrode_group",
        description="A test electrode group.",
        location="A brain region targeted by the probe insertion.",
        device=device,
        nwbfile=nwbfile,
    )
    electrodes = pynwb.testing.mock.ecephys.mock_ElectrodeTable(group=electrode_group, nwbfile=nwbfile)

    electrical_series = pynwb.testing.mock.ecephys.mock_ElectricalSeries(
        name="test_electrical_series", electrodes=electrodes
    )
    nwbfile.add_acquisition(electrical_series)

    return nwbfile


@pytest.fixture(scope="session")
def ecephys_nwbfile_path(testing_files_directory: pathlib.Path, ecephys_nwbfile: pynwb.NWBFile) -> pathlib.Path:
    ecephys_subdirectory = testing_files_directory / "ecephys"
    ecephys_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ecephys_subdirectory / "ecephys.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(ecephys_nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def trials_nwbfile() -> pynwb.NWBFile:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id="456")

    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="male",
    )
    nwbfile.subject = subject

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    return nwbfile


@pytest.fixture(scope="session")
def trials_events_nwbfile_path(testing_files_directory: pathlib.Path, trials_nwbfile: pynwb.NWBFile) -> pathlib.Path:
    events_subdirectory = testing_files_directory / "trials"
    events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = events_subdirectory / "trials.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(trials_nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def epochs_events_nwbfile_path(
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

    nwbfile_path = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_epochs.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def multiple_events_nwbfile_path(
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

    nwbfile_path = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_multiple_events.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def nwbfile_path_with_missing_session_id(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile()
    time_series = pynwb.TimeSeries(name="Test", data=numpy.array(object=[], dtype="uint8"), unit="n.a.", rate=1.0)
    nwbfile.add_acquisition(time_series)

    subject = pynwb.file.Subject(
        subject_id="12_34",
        sex="male",
    )
    nwbfile.subject = subject
    nwbfile_path = tmp_path_factory.mktemp("test_nwb2bids") / "testfile_nosessionid.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path
