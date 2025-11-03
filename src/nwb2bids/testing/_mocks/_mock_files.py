import pathlib

import pydantic
import pynwb
import pynwb.testing.mock.ecephys
import pynwb.testing.mock.file


@pydantic.validate_call
def generate_ephys_tutorial(output_directory: pydantic.DirectoryPath | None) -> pathlib.Path:
    if output_directory is None:
        # TODO: update to common home/config utility
        tutorial_dir = pathlib.Path.home() / ".nwb2bids" / "tutorials"
        tutorial_dir.mkdir(parents=True, exist_ok=True)
        output_directory = tutorial_dir / "ephys"
        output_directory.mkdir(exist_ok=True)

    nwbfile = pynwb.testing.mock.file.mock_NWBFile(
        session_description="An example NWB file containing ephys neurodata types - for use in the nwb2bids tutorials."
    )

    electrical_series = pynwb.testing.mock.ecephys.mock_ElectricalSeries(
        name="ExampleElectricalSeries",
        description=(
            "An example electrical series that represents data which could have been "
            "read off of the channels of an ephys probe."
        ),
        nwbfile=nwbfile,
    )
    nwbfile.add_acquisition(electrical_series)

    nwbfile_path = output_directory / "ephys.nwb"
    with pynwb.NWBHDF5IO(name=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)

    return nwbfile_path
