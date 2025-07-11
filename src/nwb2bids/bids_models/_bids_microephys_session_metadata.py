import pydantic
import pynwb
import typing_extensions

from ._channels import ChannelTable
from ._electrodes import ElectrodeTable
from ._events import Events
from ._participant import Participant
from ._probes import ProbeTable


class BidsSessionMetadata(pydantic.BaseModel):
    """
    Schema for the metadata of a single BIDS session.
    """

    session_id: str = pydantic.Field(
        description="A unique session identifier.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    participant: Participant = pydantic.Field(description="Metadata about a participant used in this experiment.")
    # general_metadata: GeneralMetadata = pydantic.Field(
    #     description="General metadata about the setup for this experiment."
    # )
    events: Events | None = pydantic.Field(
        description="Timing data and metadata regarding events that occur during this experiment.", default=None
    )
    probe_table: ProbeTable | None = None
    channel_table: ChannelTable | None = None
    electrode_table: ElectrodeTable | None = None

    @classmethod
    @pydantic.validate_call
    def from_nwbfile_paths(cls, nwbfile_paths: list[pydantic.FilePath]) -> typing_extensions.Self:
        nwbfiles = [pynwb.read_nwb(nwbfile_path) for nwbfile_path in nwbfile_paths]
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
