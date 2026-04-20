import pathlib
import re
import typing

import h5py
import pydantic
import pynwb
import pynwb.ecephys
import pynwb.misc
import typing_extensions

from ._base_metadata_model import BaseMetadataContainerModel
from ._channels import ChannelTable
from ._electrodes import ElectrodeTable
from ._events import Events
from ._general_metadata import GeneralMetadata
from ._model_globals import _VALID_ID_REGEX
from ._participant import Participant
from ._probes import ProbeTable
from .._converters._run_config import RunConfig
from .._tools import cache_read_nwb
from ..notifications import Notification
from ..sanitization import Sanitization


def _has_units_table(nwbfiles: list[pynwb.NWBFile]) -> bool:
    """
    Return True if any of the given NWB files contains a units table.

    Checks both the top-level ``nwbfile.units`` attribute and any
    :class:`~pynwb.misc.Units` objects stored in processing modules.
    """
    for nwbfile in nwbfiles:
        if nwbfile.units is not None:
            return True
        for processing_module in nwbfile.processing.values():
            for data_interface in processing_module.data_interfaces.values():
                if isinstance(data_interface, pynwb.misc.Units):
                    return True
    return False


def _has_electrical_series_in_acquisition(nwbfiles: list[pynwb.NWBFile]) -> bool:
    """
    Return True if any of the given NWB files contains an :class:`~pynwb.ecephys.ElectricalSeries`
    directly in the ``acquisition`` module (i.e., raw, unprocessed data).
    """
    for nwbfile in nwbfiles:
        for data_object in nwbfile.acquisition.values():
            if isinstance(data_object, pynwb.ecephys.ElectricalSeries):
                return True
    return False


class BidsSessionMetadata(BaseMetadataContainerModel):
    """
    Schema for the metadata of a single BIDS session.
    """

    session_id: str | None = pydantic.Field(description="A unique session identifier.", default=None)
    participant: Participant = pydantic.Field(description="Metadata about a participant used in this experiment.")
    general_metadata: GeneralMetadata = pydantic.Field(description="General metadata about the experiment.")
    events: Events | None = pydantic.Field(
        description="Timing data and metadata regarding events that occur during this experiment.", default=None
    )
    probe_table: ProbeTable | None = None
    electrode_table: ElectrodeTable | None = None
    channel_table: ChannelTable | None = None
    has_units_table: bool = pydantic.Field(
        description="Whether the source NWB files contain a units table (top-level or in a processing module).",
        default=False,
    )
    has_electrical_series_in_acquisition: bool = pydantic.Field(
        description="Whether the source NWB files contain an ElectricalSeries in the acquisition module.",
        default=False,
    )
    run_config: RunConfig = pydantic.Field(default_factory=RunConfig)
    sanitization: Sanitization | None = None

    def model_post_init(self, context: typing.Any, /) -> None:
        if self.sanitization is not None:
            return

        self.sanitization = Sanitization(
            sanitization_config=self.run_config.sanitization_config,
            sanitization_file_path=self.run_config.sanitization_file_path,
            original_session_id=self.session_id,
            original_participant_id=self.participant.participant_id,
        )

    @pydantic.computed_field
    @property
    def notifications(self) -> list[Notification]:
        notifications = self.participant.notifications.copy()
        notifications += self._internal_notifications.copy()
        if self.events is not None:
            notifications += self.events.notifications.copy()
        if self.probe_table is not None:
            notifications += self.probe_table.notifications
        if self.electrode_table is not None:
            notifications += self.electrode_table.notifications
        if self.channel_table is not None:
            notifications += self.channel_table.notifications
        notifications.sort(
            key=lambda notification: (-notification.category.value, -notification.severity.value, notification.title)
        )
        return notifications

    def _check_fields(self, file_paths: list[pathlib.Path] | list[pydantic.HttpUrl]) -> None:
        # Check if values are specified
        internal_messages = []
        if self.session_id is None:
            notification = Notification.from_definition(identifier="MissingSessionID", source_file_paths=file_paths)
            internal_messages.append(notification)

        # Check if specified values are valid
        if self.session_id is not None and re.match(pattern=f"{_VALID_ID_REGEX}$", string=self.session_id) is None:
            notification = Notification.from_definition(identifier="InvalidSessionID", source_file_paths=file_paths)
            internal_messages.append(notification)
        self._internal_notifications = internal_messages

    @classmethod
    @pydantic.validate_call
    def from_nwbfile_paths(
        cls,
        nwbfile_paths: list[pydantic.FilePath] | list[pydantic.HttpUrl] = pydantic.Field(min_length=1),
        run_config: RunConfig = pydantic.Field(default_factory=RunConfig),
    ) -> typing_extensions.Self:
        # Differentiate local path from URL
        if isinstance(next(iter(nwbfile_paths)), pathlib.Path):
            nwbfiles = [cache_read_nwb(nwbfile_path) for nwbfile_path in nwbfile_paths]
        else:
            nwbfiles = [_stream_nwb(url=url) for url in typing.cast(list[pydantic.HttpUrl], nwbfile_paths)]

        session_ids = {nwbfile.session_id for nwbfile in nwbfiles}
        if len(session_ids) > 1:
            message = "Multiple differing session IDs found - please check how this method was called."
            raise ValueError(message)
        session_id = next(iter(session_ids))

        participant = Participant.from_nwbfiles(nwbfiles=nwbfiles)
        general_metadata = GeneralMetadata.from_nwbfiles(nwbfiles=nwbfiles)
        events = Events.from_nwbfiles(nwbfiles=nwbfiles)
        probe_table = ProbeTable.from_nwbfiles(nwbfiles=nwbfiles, probe_name=run_config.probe)
        electrode_table = ElectrodeTable.from_nwbfiles(nwbfiles=nwbfiles)
        channel_table = ChannelTable.from_nwbfiles(nwbfiles=nwbfiles)
        has_units = _has_units_table(nwbfiles=nwbfiles)
        has_es_in_acquisition = _has_electrical_series_in_acquisition(nwbfiles=nwbfiles)

        dictionary = {
            "session_id": session_id,
            "participant": participant,
            "general_metadata": general_metadata,
            "run_config": run_config,
            "has_units_table": has_units,
            "has_electrical_series_in_acquisition": has_es_in_acquisition,
        }
        if events is not None:
            dictionary["events"] = events
        if probe_table is not None:
            dictionary["probe_table"] = probe_table
        if electrode_table is not None:
            dictionary["electrode_table"] = electrode_table
        if channel_table is not None:
            dictionary["channel_table"] = channel_table

        session_metadata = cls(**dictionary)
        session_metadata._check_fields(file_paths=nwbfile_paths)
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
