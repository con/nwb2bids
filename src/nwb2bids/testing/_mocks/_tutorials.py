import pathlib
import typing

import numpy
import pydantic
import pynwb
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file
import pynwb.testing.mock.icephys


def get_tutorial_directory() -> pathlib.Path:
    tutorial_dir = pathlib.Path.home() / "nwb2bids_tutorials"
    tutorial_dir.mkdir(exist_ok=True)
    return tutorial_dir


def _generate_ecephys_file(*, nwbfile_path: pathlib.Path, subject_id: str = "001", session_id: str = "A") -> None:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(
        session_id=session_id,
        session_description=(
            "An example NWB file containing ecephys neurodata types - for use in the nwb2bids tutorials."
        ),
    )

    subject = pynwb.file.Subject(
        subject_id=subject_id,
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    probe = pynwb.testing.mock.ecephys.mock_Device(
        name="ExampleProbe",
        description="This is an example ecephys probe used for demonstration purposes.",
        manufacturer="`nwb2bids` test suite",
        nwbfile=nwbfile,
    )
    shank = pynwb.testing.mock.ecephys.mock_ElectrodeGroup(
        name="ExampleShank",
        description="This is an example electrode group (shank) used for demonstration purposes.",
        location="hippocampus",
        device=probe,
        nwbfile=nwbfile,
    )

    number_of_electrodes = 8
    for index in range(number_of_electrodes):
        nwbfile.add_electrode(imp=150_000.0, location="hippocampus", group=shank, filtering="HighpassFilter")
    electrodes = nwbfile.create_electrode_table_region(
        region=list(range(number_of_electrodes)),
        description="A `DynamicTableRegion` referring to all electrodes in this file.",
    )

    pynwb.testing.mock.ecephys.mock_ElectricalSeries(
        name="ExampleElectricalSeries",
        description=(
            "An example electrical series that represents data which could have been "
            "read off of the channels of an ecephys probe."
        ),
        data=numpy.ones(shape=(10, number_of_electrodes)),
        electrodes=electrodes,
        rate=30_000.0,
        nwbfile=nwbfile,
        conversion=0.00000302734375,
    )

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)


def _generate_icephys_file(*, nwbfile_path: pathlib.Path, subject_id: str = "001", session_id: str = "A") -> None:
    nwbfile = pynwb.testing.mock.file.mock_NWBFile(
        session_id=session_id,
        session_description=(
            "An example NWB file containing icephys neurodata types - for use in the nwb2bids tutorials."
        ),
    )

    subject = pynwb.file.Subject(
        subject_id=subject_id,
        species="Mus musculus",
        sex="M",
    )
    nwbfile.subject = subject

    # Icephys 'probes'
    probe1 = pynwb.testing.mock.icephys.mock_Device(
        name="pipette01",
        description="This is an example icephys probe used for demonstration purposes.",
        manufacturer="Sutter",
        nwbfile=nwbfile,
    )
    probe2 = pynwb.testing.mock.icephys.mock_Device(
        name="pipette02",
        description="This is an example icephys probe used for demonstration purposes.",
        manufacturer="Sutter",
        nwbfile=nwbfile,
    )
    probe3 = pynwb.testing.mock.icephys.mock_Device(
        name="pipette03",
        description="This is an example icephys probe used for demonstration purposes.",
        manufacturer="WPI",
        nwbfile=nwbfile,
    )

    # Icephys electrodes
    electrode1 = nwbfile.create_icephys_electrode(
        name="patch01",
        description="This is an example icephys electrode used for demonstration purposes.",
        device=probe1,
        location="VISp2/3",
    )
    electrode2 = nwbfile.create_icephys_electrode(
        name="patch02",
        description="This is an example icephys electrode used for demonstration purposes.",
        device=probe2,
        location="VISp2/3",
    )
    electrode3 = nwbfile.create_icephys_electrode(
        name="sharp01",
        description="This is an example icephys electrode used for demonstration purposes.",
        device=probe3,
        location="PL5",
    )

    # Icephys series
    series1 = pynwb.testing.mock.icephys.mock_CurrentClampSeries(
        name="ExampleCurrentClampSeries1",
        data=[-70, -60, -50, -40, -30],
        conversion=1e-3,
        resolution=numpy.nan,
        rate=20e3,
        electrode=electrode1,
        gain=0.01,
        bias_current=1e-12,
        bridge_balance=70e6,
        capacitance_compensation=1e-12,
    )
    series2 = pynwb.testing.mock.icephys.mock_CurrentClampSeries(
        name="ExampleCurrentClampSeries2",
        data=[-10, 0, 10, 20, 30],
        conversion=1e-3,
        resolution=numpy.nan,
        rate=20e3,
        electrode=electrode2,
        gain=0.01,
        bias_current=1e-12,
        bridge_balance=70e6,
        capacitance_compensation=1e-12,
    )
    nwbfile.add_intracellular_recording(electrode=electrode1, response=series1)
    nwbfile.add_intracellular_recording(electrode=electrode2, response=series2)

    pynwb.testing.mock.icephys.mock_VoltageClampSeries(
        name="ExampleVoltageClampSeries1",
        data=[1.0, 2.0, 3.0, 4.0, 5.0],
        conversion=1e-12,
        resolution=numpy.nan,
        rate=20e3,
        electrode=electrode3,
        gain=5e-12,
        capacitance_slow=100e-12,
        resistance_comp_correction=70.0,
        nwbfile=nwbfile,
    )

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)


@pydantic.validate_call
def generate_ephys_tutorial(
    *,
    mode=typing.Literal["file", "dataset"],
    output_directory: pydantic.DirectoryPath | None = None,
    modality: typing.Literal["ecephys", "icephys"] = "ecephys",
) -> pathlib.Path:
    if output_directory is None:
        tutorial_dir = get_tutorial_directory()
        output_directory = tutorial_dir / f"{modality}_tutorial_{mode}"
        output_directory.mkdir(exist_ok=True)

    if mode == "file":
        nwbfile_path = output_directory / f"{modality}.nwb"

        if modality == "ecephys":
            _generate_ecephys_file(nwbfile_path=nwbfile_path)
        else:
            _generate_icephys_file(nwbfile_path=nwbfile_path)

        return nwbfile_path

    subdir = output_directory / "some_sessions"
    subdir.mkdir(exist_ok=True)
    index_to_paths = {
        0: subdir / f"{modality}_session_1.nwb",
        1: subdir / f"{modality}_session_2.nwb",
        2: output_directory / f"{modality}_session_3.nwb",
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

        if modality == "ecephys":
            _generate_ecephys_file(
                nwbfile_path=nwbfile_path, subject_id=index_to_subject_id[index], session_id=index_to_session_id[index]
            )
        else:
            _generate_icephys_file(
                nwbfile_path=nwbfile_path, subject_id=index_to_subject_id[index], session_id=index_to_session_id[index]
            )

    return output_directory
