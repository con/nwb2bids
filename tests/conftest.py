import datetime
import json
import os
import pathlib
import shutil
import subprocess
import uuid
from collections.abc import Callable

import py.path
import pynwb
import pynwb.file
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file
import pytest

import nwb2bids

# TODO: add DynamicTable's in acquisition with *_time columns


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--container-image",
        action="store",
        default=None,
        help="Docker/container image to test CLI against (e.g., nwb2bids:dev)",
    )


def pytest_report_header(config: pytest.Config) -> str | None:
    image = config.getoption("--container-image")
    if image:
        return f"container image: {image}"
    return None


@pytest.fixture(scope="session")
def container_image(request: pytest.FixtureRequest) -> str | None:
    """Returns the container image specified via --container-image, or None."""
    return request.config.getoption("--container-image")


@pytest.fixture(scope="session")
def cli_runner(
    tmp_path_factory: pytest.TempPathFactory,
    container_image: str | None,
) -> Callable[[str], subprocess.CompletedProcess]:
    """
    Returns a function to run CLI commands.

    If --container-image is specified, commands run inside the container
    with the pytest temp directory bind-mounted.
    """
    basetemp = tmp_path_factory.getbasetemp()

    if container_image:
        uid, gid = os.getuid(), os.getgid()
        # Set HOME to basetemp so ~/.cache and ~/.nwb2bids resolve to writable locations
        prefix = (
            f"docker run --rm --user {uid}:{gid} "
            f"-v {basetemp}:{basetemp} "
            f"-e HOME={basetemp} "
            f"{container_image}"
        )
    else:
        prefix = ""

    def run(command: str) -> subprocess.CompletedProcess:
        full_command = f"{prefix} {command}" if prefix else command
        return subprocess.run(args=full_command, shell=True, capture_output=True)

    return run


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


@pytest.fixture(scope="function")
def temporary_run_directory(tmpdir: py.path.local) -> pathlib.Path:
    """Creates a temporary working directory for testing purposes."""
    return pathlib.Path(tmpdir)


@pytest.fixture(scope="function")
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
            "HEDVersion": "8.3.0",
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
            "HEDVersion": "8.3.0",
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
def ecephys_tutorial_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    ecephys_subdirectory = testing_files_directory / "ecephys"
    ecephys_subdirectory.mkdir(exist_ok=True)

    nwbfile_path = nwb2bids.testing.generate_ephys_tutorial(mode="file", output_directory=ecephys_subdirectory)
    return nwbfile_path


@pytest.fixture(scope="session")
def ecephys_minimal_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(
        session_id="A",
        session_description=(
            "An example NWB file containing ecephys neurodata types which has only the "
            "minimum number of fields specified."
        ),
    )

    subject = pynwb.file.Subject(
        subject_id="001",
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    probe = pynwb.testing.mock.ecephys.mock_Device(
        name="ExampleProbe",
        description="This is an example probe used for demonstration purposes.",
        nwbfile=nwbfile,
    )
    shank = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(
        name="ExampleShank",
        description="This is an example electrode group (shank) used for demonstration purposes.",
        device=probe,
        nwbfile=nwbfile,
    )

    number_of_electrodes = 8
    for index in range(number_of_electrodes):
        nwbfile.add_electrode(location="n/a", group=shank)

    # Not even including an ElectricalSeries - just metadata

    ecephys_subdirectory = testing_files_directory / "ecephys"
    ecephys_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ecephys_subdirectory / "ecephys_minimal.nwb"
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
    nwbfile.add_electrode(group=group, location="n/a")

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


@pytest.fixture(scope="session")
def ndx_events_table_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """An NWB file containing an ndx-events EventsTable (timestamps only, no duration)."""
    nwbfile = _make_minimal_nwbfile()

    events_table = nwb2bids.testing.mock_events_table()
    nwbfile.add_acquisition(events_table)

    ndx_events_subdirectory = testing_files_directory / "ndx_events"
    ndx_events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ndx_events_subdirectory / "ndx_events_table.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ndx_events_table_with_duration_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """An NWB file containing an ndx-events EventsTable with timestamps and duration (some NaN)."""
    nwbfile = _make_minimal_nwbfile()

    events_table = nwb2bids.testing.mock_events_table_with_duration()
    nwbfile.add_acquisition(events_table)

    ndx_events_subdirectory = testing_files_directory / "ndx_events"
    ndx_events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ndx_events_subdirectory / "ndx_events_table_with_duration.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ndx_events_table_with_label_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """An NWB file containing an ndx-events EventsTable with timestamps and a label column."""
    nwbfile = _make_minimal_nwbfile()

    events_table = nwb2bids.testing.mock_events_table_with_label()
    nwbfile.add_acquisition(events_table)

    ndx_events_subdirectory = testing_files_directory / "ndx_events"
    ndx_events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ndx_events_subdirectory / "ndx_events_table_with_label.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path


@pytest.fixture(scope="session")
def ndx_events_mixed_with_time_intervals_nwbfile_path(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """An NWB file containing both an ndx-events EventsTable and a TimeIntervals table."""
    nwbfile = _make_minimal_nwbfile()

    trials = nwb2bids.testing.mock_trials_table()
    nwbfile.trials = trials

    events_table = nwb2bids.testing.mock_events_table()
    nwbfile.add_acquisition(events_table)

    ndx_events_subdirectory = testing_files_directory / "ndx_events"
    ndx_events_subdirectory.mkdir(exist_ok=True)
    nwbfile_path = ndx_events_subdirectory / "ndx_events_mixed.nwb"
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path
  
@pytest.fixture(scope="session")
def directory_with_multiple_subjects_and_multiple_sessions(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A directory containing NWB files for multiple subjects each with multiple sessions.

    Used to test that the `ses-` label is applied when subjects have multiple sessions.
    Subject IDs: "subA" (sessions A1 and A2), "subB" (sessions B1 and B2).
    Session IDs are unique across subjects to avoid grouping issues.
    """
    subdirectory = testing_files_directory / "multiple_subjects_multiple_sessions"
    subdirectory.mkdir(exist_ok=True)

    for subject_index in ["A", "B"]:
        for session_index in [1, 2]:
            nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id=f"sub{subject_index}session{session_index}")
            nwbfile.subject = pynwb.file.Subject(
                subject_id=f"sub{subject_index}",
                species="Mus musculus",
                sex="M",
            )
            nwbfile_path = subdirectory / f"subject_{subject_index}_session_{session_index}.nwb"
            with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
                file_stream.write(nwbfile)

    return subdirectory


@pytest.fixture(scope="session")
def directory_with_mixed_session_counts(testing_files_directory: pathlib.Path) -> pathlib.Path:
    """
    A directory where the majority (>50%) of subjects have multiple sessions.

    Used to test the 50% consistency rule: if >50% of subjects have multiple sessions,
    all subjects (including single-session ones) should use the `ses-` label.

    Subject "subX": 2 sessions (X1, X2)
    Subject "subY": 2 sessions (Y1, Y2)
    Subject "subZ": 1 session (Z1) - single-session, but should still get ses- label
    Session IDs are unique across subjects to avoid grouping issues.
    """
    subdirectory = testing_files_directory / "mixed_session_counts"
    subdirectory.mkdir(exist_ok=True)

    for subject_id, session_ids in [("subX", ["X1", "X2"]), ("subY", ["Y1", "Y2"]), ("subZ", ["Z1"])]:
        for session_id in session_ids:
            nwbfile = pynwb.testing.mock.file.mock_NWBFile(session_id=session_id)
            nwbfile.subject = pynwb.file.Subject(
                subject_id=subject_id,
                species="Mus musculus",
                sex="M",
            )
            nwbfile_path = subdirectory / f"{subject_id}_{session_id}.nwb"
            with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
                file_stream.write(nwbfile)

    return subdirectory
