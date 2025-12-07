import datetime
import json
import os
import pathlib
import shutil
import sys
import uuid

import py.path
import pynwb
import pynwb.file
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file
import pytest

import nwb2bids

# These tests fail on Windows GitHub CI due to git-annex adjusted branch issues
# See https://github.com/con/nwb2bids/pull/213 for failure output
pytest_mark_xfail_windows_github_ci = pytest.mark.xfail(
    sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS", "").lower() == "true",
    reason="git-annex adjusted branch fails on Windows GitHub CI runners",
    strict=False,
)

# TODO: add ndx-events
# TODO: add DynamicTable's in acquisition with *_time columns


def _make_minimal_nwbfile(session_id: str = "456", subject_species: str = "Mus musculus") -> pynwb.NWBFile:
    """Creates a minimal NWB file for testing purposes."""
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id=session_id)

    subject = pynwb.file.Subject(
        subject_id="123",
        species=subject_species,
        sex="M",
    )
    nwbfile.subject = subject

    return nwbfile


@pytest.fixture()
def temporary_run_directory(tmpdir: py.path.local) -> pathlib.Path:
    """Creates a temporary working directory for testing purposes."""
    return pathlib.Path(tmpdir)


@pytest.fixture()
def temporary_bids_directory(temporary_run_directory: pathlib.Path) -> pathlib.Path:
    """Creates a temporary BIDS directory for testing purposes."""
    bids_directory = temporary_run_directory / "bids"
    bids_directory.mkdir(exist_ok=True)
    return bids_directory


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
def additional_metadata_with_generated_by_file_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    additional_metadata_dictionary = {
        "dataset_description": {
            "Name": "test",
            "Description": "Dataset with user-provided GeneratedBy",
            "BIDSVersion": "1.10",
            "DatasetType": "raw",
            "License": "CC-BY-4.0",
            "Authors": ["Cody Baker", "Yaroslav Halchenko"],
            "GeneratedBy": [
                {
                    "Name": "custom-pipeline",
                    "Version": "1.0.0",
                    "Description": "Custom data processing pipeline",
                    "CodeURL": "https://github.com/example/custom-pipeline",
                }
            ],
        }
    }

    additional_metadata_subdirectory = testing_files_directory / "additional_metadata"
    additional_metadata_subdirectory.mkdir(exist_ok=True)
    file_path = additional_metadata_subdirectory / "test_additional_metadata_with_generated_by.json"
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
def minimal_mismatch_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    Prior to PR #???, it was possible to create `participants.tsv` files with duplicated `participant_id` values.

    This was because of the way dataframes were merged during the creation of the participants table.
    """
    nwbfile = _make_minimal_nwbfile(session_id="4567", subject_species="mouse")

    minimal_subdirectory = testing_files_directory / "minimal_mismatch"
    minimal_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = minimal_subdirectory / "minimal_mismatch.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ecephys_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = _make_minimal_nwbfile(session_id="789")

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

    trials = nwb2bids.testing.mock_trials_table(nwbfile=nwbfile)
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
def directory_with_multiple_nwbfiles(testing_files_directory: pathlib.Path) -> pathlib.Path:
    multiple_nwbfiles_subdirectory = testing_files_directory / "multiple_nwbfiles"
    multiple_nwbfiles_subdirectory.mkdir(exist_ok=True)

    for session_index in range(2):
        nwbfile = _make_minimal_nwbfile(session_id=f"session-{session_index}")

        nwbfile_path = multiple_nwbfiles_subdirectory / f"session_{session_index}.nwb"
        with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
            file_stream.write(nwbfile)

    return multiple_nwbfiles_subdirectory


@pytest.fixture(scope="session")
def mock_datalad_dataset(testing_files_directory: pathlib.Path, minimal_nwbfile_path: pathlib.Path) -> pathlib.Path:
    """
    A mock datalad dataset for testing purposes.

    Original globbing pattern was too broad and found files within the git-annex.
    """
    dataset_subdirectory = testing_files_directory / "mock_datalad_dataset"
    dataset_subdirectory.mkdir(exist_ok=True)

    annex_filename = "MD5E-s14336--bd0eed310fabd903a2635186e06b6a43.nwb"
    structure = {
        ".datalad": {
            ".gitattributes": "config annex.largefiles=nothing\n",
            "config": '[datalad "dataset"]\n\tid = NOT-A-REAL-DATALAD-DATASET',
        },
        ".git": {"annex": {"objects": {"abc": {"def": {annex_filename: {annex_filename: ""}}}}}},
    }
    nwb2bids.testing.create_file_tree(directory=dataset_subdirectory, structure=structure)

    content_file_path = dataset_subdirectory / ".git/annex/objects/abc/def" / annex_filename / annex_filename
    shutil.copy2(src=minimal_nwbfile_path, dst=content_file_path)

    annexed_file_path = dataset_subdirectory / "minimal.nwb"
    annexed_file_path.symlink_to(target=content_file_path)

    return dataset_subdirectory


# Problematic test cases
@pytest.fixture(scope="session")
def problematic_nwbfile_path_1(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    An NWB file with 'problematic' metadata for testing the messaging feature.
    """
    nwbfile = pynwb.NWBFile(
        identifier="not a UUID",
        session_id="problematic1",
        session_description="",
        session_start_time=datetime.datetime.now().astimezone(),
    )

    subject = pynwb.file.Subject(
        subject_id="bad_subject_id",
        species="not a latin species, nor a ncbi taxon link or id",
        sex="bad sex specifier",
    )
    nwbfile.subject = subject

    problematic_subdirectory = testing_files_directory / "problematic"
    problematic_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = problematic_subdirectory / "problematic1.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def problematic_nwbfile_path_2(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A second NWB file with 'problematic' metadata for testing the messaging feature.
    """
    nwbfile = pynwb.NWBFile(
        identifier="not a UUID",
        session_id="#problematic!2~",
        session_description="",
        session_start_time=datetime.datetime.now().astimezone(),
    )

    subject = pynwb.file.Subject(
        subject_id="bad subject id",
    )
    nwbfile.subject = subject

    problematic_subdirectory = testing_files_directory / "problematic"
    problematic_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = problematic_subdirectory / "problematic2.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def problematic_nwbfile_path_3(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A third NWB file with 'problematic' metadata (entirely missing entities) for testing the messaging feature.
    """
    nwbfile = pynwb.NWBFile(
        identifier="not a UUID",
        session_id="problematic3",
        session_description="",
        session_start_time=datetime.datetime.now().astimezone(),
    )

    problematic_subdirectory = testing_files_directory / "problematic"
    problematic_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = problematic_subdirectory / "problematic3.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def problematic_nwbfile_path_4(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A fourth NWB file with less problematic metadata corresponding only to low-level 'info' events.
    """
    nwbfile = pynwb.NWBFile(
        identifier=str(uuid.uuid4()),
        session_id="problematic4",
        session_description="",
        session_start_time=datetime.datetime.now().astimezone(),
    )
    subject = pynwb.file.Subject(
        subject_id="123",
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    device = pynwb.testing.mock.ecephys.mock_Device(name="DeviceWithoutDescription", description=None, nwbfile=nwbfile)
    group = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(device=device, nwbfile=nwbfile)
    nwbfile.add_electrode(group=group, location="unknown")

    problematic_subdirectory = testing_files_directory / "problematic"
    problematic_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = problematic_subdirectory / "problematic4.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def problematic_nwbfile_path_missing_session_id(testing_files_directory: pathlib.Path) -> pathlib.Path:
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
