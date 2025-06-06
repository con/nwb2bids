import pynwb
import numpy
import pytest
from datetime import datetime
from dateutil import tz


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
def nwb_testdata_nosessionid(
    tmp_path_factory,
):
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
    filename = tmp_path_factory.mktemp("test_nwb2bids") / "testfile.nwb"
    with pynwb.NWBHDF5IO(path=filename, mode="w") as io:
        io.write(nwbfile)

    return filename
