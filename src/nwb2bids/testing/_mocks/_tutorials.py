import pathlib
import typing

import pydantic
import pynwb
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file

from ..._core._home import _get_home_directory


def get_tutorial_directory() -> pathlib.Path:
    tutorial_dir = _get_home_directory() / "tutorials"
    tutorial_dir.mkdir(exist_ok=True)
    return tutorial_dir


def _generate_ecephys_file(
    *, nwbfile_path: pathlib.Path, subject_id: str = "001", session_id: str = "session+1"
) -> None:
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

    pynwb.testing.mock.ecephys.mock_ElectricalSeries(
        name="ExampleElectricalSeries",
        description=(
            "An example electrical series that represents data which could have been "
            "read off of the channels of an ephys probe."
        ),
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
            2: "subject+2",
            3: "subject+3",
        }

        for index in range(4):
            nwbfile_path = index_to_paths[index]
            _generate_ecephys_file(
                nwbfile_path=nwbfile_path, subject_id=index_to_subject_id[index], session_id=f"session+{index+1}"
            )

        return output_directory
