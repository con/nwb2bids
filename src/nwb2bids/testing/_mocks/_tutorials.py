import itertools
import pathlib
import typing

import pydantic
import pynwb
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file


def get_tutorial_directory() -> pathlib.Path:
    tutorial_dir = pathlib.Path.home() / "nwb2bids_tutorials"
    tutorial_dir.mkdir(exist_ok=True)
    return tutorial_dir


def _generate_ecephys_file(*, nwbfile_path: pathlib.Path, subject_id: str = "001", session_id: str = "A") -> None:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(
        session_id=session_id,
        session_description="An example NWB file containing ephys neurodata types - for use in the nwb2bids tutorials.",
    )

    subject = pynwb.file.Subject(
        subject_id=subject_id,
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    probe1 = pynwb.testing.mock.ecephys.mock_Device(
        name="probe01",
        description="This is an example probe used for demonstration purposes.",
        manufacturer="IMEC",
        nwbfile=nwbfile,
    )
    probe2 = pynwb.testing.mock.ecephys.mock_Device(
        name="probe02",
        description="This is an example probe used for demonstration purposes.",
        manufacturer="Neuralynx",
        nwbfile=nwbfile,
    )
    shank1 = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(
        name="ExampleShank1",
        description="This is an example electrode group (shank) used for demonstration purposes.",
        location="left MOp",
        device=probe1,
        position=(1000, 2000, 3000),
        nwbfile=nwbfile,
    )
    shank2 = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(
        name="ExampleShank2",
        description="This is an example electrode group (shank) used for demonstration purposes.",
        location="right CA1",
        device=probe2,
        position=(3000, 4000, 5000),
        nwbfile=nwbfile,
    )

    # Chosen to be as close as possible to BIDS specification examples
    electrode_properties_probe1 = [
        {"imp": 1, "location": "left MOp", "group": shank1},
        {"imp": 2, "location": "left MOp", "group": shank1},
        {"imp": 3, "location": "left MOp", "group": shank1},
        {"imp": 4, "location": "left MOp", "group": shank1},
    ]
    electrode_properties_probe2 = [
        {"imp": 1, "location": "right CA1", "group": shank2},
        {"imp": 2, "location": "right CA1", "group": shank2},
        {"imp": 3, "location": "right CA1", "group": shank2},
        {"imp": 4, "location": "right CA1", "group": shank2},
    ]
    for electrode_kwargs in itertools.chain(electrode_properties_probe1, electrode_properties_probe2):
        nwbfile.add_electrode(**electrode_kwargs)

    electrodes = nwbfile.create_electrode_table_region(
        region=list(range(len(electrode_properties_probe1))),
        description="A `DynamicTableRegion` referring to the electrodes of probe01.",
    )
    pynwb.testing.mock.ecephys.mock_ElectricalSeries(
        name="ExampleElectricalSeries",
        description=(
            "An example electrical series that represents data which could have been "
            "read off of the channels of an ecephys probe."
        ),
        electrodes=electrodes,
        nwbfile=nwbfile,
    )

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)


@pydantic.validate_call
def generate_ephys_tutorial(
    *, mode=typing.Literal["file", "dataset"], output_directory: pydantic.DirectoryPath | None = None
) -> pathlib.Path:
    if output_directory is None:
        tutorial_dir = get_tutorial_directory()
        output_directory = tutorial_dir / f"ephys_tutorial_{mode}"
        output_directory.mkdir(exist_ok=True)

    if mode == "file":
        nwbfile_path = output_directory / "ephys.nwb"
        _generate_ecephys_file(nwbfile_path=nwbfile_path)

        return nwbfile_path
    elif mode == "dataset":
        subdir = output_directory / "some_sessions"
        subdir.mkdir(exist_ok=True)
        index_to_paths = {
            0: output_directory / subdir / "ephys_session_1.nwb",
            1: output_directory / subdir / "ephys_session_2.nwb",
            2: output_directory / "ephys_session_3.nwb",
            3: output_directory / "DO_NOT_CONVERT.nwb",
        }
        index_to_subject_id = {
            0: "001",
            1: "001",
            2: "002",
            3: "003",
        }
        index_to_session_id = {
            0: "A",
            1: "B",
            2: "C",
            3: "D",
        }

        for index in range(4):
            nwbfile_path = index_to_paths[index]
            _generate_ecephys_file(
                nwbfile_path=nwbfile_path, subject_id=index_to_subject_id[index], session_id=index_to_session_id[index]
            )

        return output_directory
