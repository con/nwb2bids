import pathlib
import re
import typing

import h5py
import pydantic
import pynwb
import typing_extensions

from ._base_metadata_model import BaseMetadataContainerModel
from ._channels import ChannelTable
from ._electrodes import ElectrodeTable
from ._events import Events
from ._model_globals import _VALID_ID_REGEX
from ._participant import Participant
from ._probes import ProbeTable
from .._converters._run_config import RunConfig
from .._inspection._inspection_result import Category, DataStandard, InspectionResult, Severity
from .._tools import cache_read_nwb
from ..sanitization import Sanitization


class BidsSessionMetadata(BaseMetadataContainerModel):
    """
    Schema for the metadata of a single BIDS session.
    """

    session_id: str | None = pydantic.Field(description="A unique session identifier.", default=None)
    participant: Participant = pydantic.Field(description="Metadata about a participant used in this experiment.")
    events: Events | None = pydantic.Field(
        description="Timing data and metadata regarding events that occur during this experiment.", default=None
    )
    probe_table: ProbeTable | None = None
    electrode_table: ElectrodeTable | None = None
    channel_table: ChannelTable | None = None
    run_config: RunConfig = pydantic.Field(default_factory=RunConfig)
    sanitization: Sanitization | None = None

    def model_post_init(self, context: typing.Any, /) -> None:
        """Apply sanitization (even if level 0)."""
        if self.sanitization is not None:
            return

        self.sanitization = Sanitization(
            sanitization_level=self.run_config.sanitization_level,
            sanitization_file_path=self.run_config.sanitization_file_path,
            original_session_id=self.session_id,
            original_participant_id=self.participant.participant_id,
        )

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        messages = self.participant.messages.copy()
        messages += self._internal_messages.copy()
        if self.events is not None:
            messages += self.events.messages.copy()
        if self.probe_table is not None:
            messages += self.probe_table.messages
        if self.electrode_table is not None:
            messages += self.electrode_table.messages
        if self.channel_table is not None:
            messages += self.channel_table.messages
        messages.sort(key=lambda message: (-message.category.value, -message.severity.value, message.title))
        return messages

    def _check_fields(self, file_paths: list[pathlib.Path] | list[pydantic.HttpUrl]) -> None:
        # Check if values are specified
        internal_messages = []
        if self.session_id is None:
            internal_messages.append(
                InspectionResult(
                    title="Missing session ID",
                    reason="A unique ID is required for all individual sessions.",
                    solution="Specify the `session_id` field of the NWB file object.",
                    field="nwbfile.session_id",
                    source_file_paths=file_paths,
                    data_standards=[DataStandard.BIDS, DataStandard.DANDI],
                    category=Category.SCHEMA_INVALIDATION,
                    severity=Severity.CRITICAL,
                )
            )

        # Check if specified values are valid
        if self.session_id is not None and re.match(pattern=f"{_VALID_ID_REGEX}$", string=self.session_id) is None:
            internal_messages.append(
                InspectionResult(
                    title="Invalid session ID",
                    reason=(
                        "The session ID contains invalid characters. "
                        "BIDS allows only the plus sign to be used as a separator in the subject entity label. "
                        "Underscores, dashes, spaces, slashes, and other special characters (including #) are "
                        "expressly forbidden."
                    ),
                    solution="Rename the session without using any special characters except for `+`.",
                    examples=[
                        "`ses_01` -> `ses+01`",
                        "`session #2` -> `session+2`",
                        "`id 2 from 9/1/25` -> `id+2+9+1+25`",
                    ],
                    field="nwbfile.session_id",
                    source_file_paths=file_paths,
                    data_standards=[DataStandard.BIDS, DataStandard.DANDI],
                    category=Category.STYLE_SUGGESTION,
                    severity=Severity.ERROR,
                )
            )
        self._internal_messages = internal_messages

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
            nwbfiles = [_stream_nwb(url=url) for url in nwbfile_paths]

        session_ids = {nwbfile.session_id for nwbfile in nwbfiles}
        if len(session_ids) > 1:
            message = "Multiple differing session IDs found - please check how this method was called."
            raise ValueError(message)
        session_id = next(iter(session_ids))

        participant = Participant.from_nwbfiles(nwbfiles=nwbfiles)
        events = Events.from_nwbfiles(nwbfiles=nwbfiles)
        probe_table = ProbeTable.from_nwbfiles(nwbfiles=nwbfiles)
        electrode_table = ElectrodeTable.from_nwbfiles(nwbfiles=nwbfiles)
        channel_table = ChannelTable.from_nwbfiles(nwbfiles=nwbfiles)

        dictionary = {
            "session_id": session_id,
            "participant": participant,
            "run_config": run_config,
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
