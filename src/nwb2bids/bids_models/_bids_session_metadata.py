import pathlib

import h5py
import pydantic
import pynwb
import typing_extensions

from ._base_metadata_model import BaseMetadataModel
from ._channels import ChannelTable
from ._electrodes import ElectrodeTable
from ._events import Events
from ._participant import Participant
from ._probes import ProbeTable


class BidsSessionMetadata(BaseMetadataModel):
    """
    Schema for the metadata of a single BIDS session.
    """

    session_id: str = pydantic.Field(
        description="A unique session identifier.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    participant: Participant = pydantic.Field(description="Metadata about a participant used in this experiment.")
    events: Events | None = pydantic.Field(
        description="Timing data and metadata regarding events that occur during this experiment.", default=None
    )
    probe_table: ProbeTable | None = None
    channel_table: ChannelTable | None = None
    electrode_table: ElectrodeTable | None = None

    @classmethod
    @pydantic.validate_call
    def from_nwbfile_paths(
        cls, nwbfile_paths: list[pydantic.FilePath] | list[pydantic.HttpUrl]
    ) -> typing_extensions.Self:
        # Differentiate local path from URL
        if isinstance(nwbfile_paths[0], pathlib.Path):
            nwbfiles = [pynwb.read_nwb(path=nwbfile_path) for nwbfile_path in nwbfile_paths]
        else:
            nwbfiles = [_stream_nwb(url=url) for url in nwbfile_paths]

        session_ids = list({nwbfile.session_id for nwbfile in nwbfiles})
        if len(session_ids) > 1:
            message = "Multiple differing session IDs found - please check how this method was called."
            raise ValueError(message)
        session_id = session_ids[0]

        participant = Participant.from_nwbfiles(nwbfiles=nwbfiles)
        events = Events.from_nwbfiles(nwbfiles=nwbfiles)
        probe_table = ProbeTable.from_nwbfiles(nwbfiles=nwbfiles)
        channel_table = ChannelTable.from_nwbfiles(nwbfiles=nwbfiles)
        electrode_table = ElectrodeTable.from_nwbfiles(nwbfiles=nwbfiles)

        dictionary = {
            "session_id": session_id,
            "participant": participant,
        }
        if events is not None:
            dictionary["events"] = events
        if probe_table is not None:
            dictionary["probe_table"] = probe_table
        if channel_table is not None:
            dictionary["channel_table"] = channel_table
        if electrode_table is not None:
            dictionary["electrode_table"] = electrode_table

        session_metadata = BidsSessionMetadata(**dictionary)
        return session_metadata


def _stream_nwb(url: pydantic.HttpUrl) -> pynwb.NWBFile:
    """
    Stream an NWB file from a URL using remfile.

    Parameters
    ----------
    url : pydantic.HttpUrl
        The URL of the NWB file to stream.

    Returns
    -------
    pynwb.NWBFile
        The streamed NWB file.
    """
    import remfile

    rem_file = remfile.File(url=str(url))

    try:
        h5py_file = h5py.File(name=rem_file, mode="r")
    except Exception as exception:
        message = (
            f"\nFailed to open NWB file from URL {url}: {exception}\n\n"
            "Possible that backend is not supported.\n"
            "Please raise an issue on https://github.com/con/nwb2bids/issues/new to discuss."
        )
        raise ValueError(message)

    file_io = pynwb.NWBHDF5IO(file=h5py_file, mode="r")
    nwbfile = file_io.read()
    return nwbfile
