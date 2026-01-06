import json
import pathlib
import typing
import warnings

import pandas
import pydantic
import pynwb
import typing_extensions

from nwb2bids.notifications._inspection_result import InspectionResult

from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel


class Channel(BaseMetadataModel):
    channel_name: str
    reference: str
    type: str = "N/A"
    unit: str = "V"
    sampling_frequency: float | None = None
    channel_label: str | None = None
    stream_id: str | None = None
    description: str | None = None
    hardware_filters: str = "N/A"
    software_filters: str = "N/A"
    status: typing.Literal["good", "bad"] | None = None
    status_description: str | None = None
    gain: float | None = None
    time_offset: float | None = None
    time_reference_channels: str | None = None
    ground: str | None = None
    # recording_mode: str | None = None  # TODO: icephys only


class ChannelTable(BaseMetadataContainerModel):
    channels: list[Channel]

    @pydantic.computed_field
    @property
    def notifications(self) -> list[InspectionResult]:
        """
        All notifications from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        notifications = [notification for channel in self.channels for notification in channel.notifications]
        notifications.sort(
            key=lambda notification: (-notification.category.value, -notification.severity.value, notification.title)
        )
        return notifications

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        nwbfile = nwbfiles[0]

        if not nwbfile.electrodes:
            return None

        # Only scan electrical series listed under acquisition since those under processing can downsample the rate
        sampling_frequency = None
        stream_id = None
        gain = None
        raw_electrical_series = [
            neurodata_object
            for neurodata_object in nwbfile.objects.values()
            if isinstance(neurodata_object, pynwb.ecephys.ElectricalSeries)
        ]
        if len(raw_electrical_series) > 1:
            # TODO: form a map of electrode to rate/gate based on ElectricalSeries linkage
            message = (
                "Support for automatic extraction of rates/gains from multiple ElectricalSeries is not yet "
                "implemented. Skipping `sampling_frequency`, `stream_id`, and `gain` extraction."
            )
            warnings.warn(message=message, stacklevel=2)

        if len(raw_electrical_series) == 1:
            electrical_series = raw_electrical_series[0]
            if electrical_series.rate is None:
                message = (
                    "Support for automatic extraction of rate from ElectricalSeries with timestamps "
                    "is not yet implemented. Skipping `sampling_frequency`, `stream_id`, and `gain` extraction."
                )
                warnings.warn(message=message, stacklevel=2)

            sampling_frequency = electrical_series.rate
            stream_id = electrical_series.name
            gain = electrical_series.conversion

        channels = [
            Channel(
                channel_name=(
                    f"ch{channel_name.values[0]}"
                    if (channel_name := electrode.get("channel_name", None)) is not None
                    else f"ch{electrode.index[0]}"
                ),
                reference=(
                    f"contact{contact_ids.values[0]}"  # TODO: do a deep dive into edge cases of this reference
                    if (contact_ids := electrode.get("contact_ids", None)) is not None
                    else f"e{electrode.index[0]}"
                ),
                type="N/A",  # TODO: in dedicated follow-up, could classify LFP based on container
                unit="V",
                sampling_frequency=sampling_frequency,
                # channel_label: str | None = None # TODO: only support with additional metadata
                stream_id=stream_id,
                # description: str | None = None  # TODO: only support with additional metadata
                hardware_filters=(
                    filter.values[0] if (filter := electrode.get("filtering", None)) is not None else "N/A"
                ),
                # software_filters: str = "N/A" # TODO: only support with additional metadata
                # status: typing.Literal["good", "bad"] | None = None # TODO: only support with additional metadata
                # status_description: str | None = None # TODO: only support with additional metadata
                gain=gain,
                # Special extraction from SpikeInterface field
                time_offset=shift[0] if (shift := electrode.get("inter_sample_shift", None)) is not None else None,
                # time_reference_channels: str | None = None # TODO: only support with additional metadata
                # ground: str | None = None # TODO: only support with additional metadata
            )
            for electrode in nwbfile.electrodes
        ]
        return cls(channels=channels)

    @pydantic.validate_call
    def to_tsv(self, file_path: str | pathlib.Path):
        """
        Write the channels data to a TSV file.

        Parameters
        ----------
        file_path : path
            The path where the TSV file will be saved.
        """
        data = []
        for channel in self.channels:
            model_dump = channel.model_dump()
            data.append(model_dump)

        data_frame = pandas.DataFrame(data=data)
        columns_to_drop = [  # Special rule for non-required fields that autopopulate with "N/A"
            column for column in ["hardware_filters", "software_filters"] if (data_frame[column] == "N/A").all()
        ]
        data_frame = data_frame.drop(columns=columns_to_drop)
        data_frame = data_frame.dropna(axis=1, how="all")
        data_frame.to_csv(path_or_buf=file_path, sep="\t", index=False)

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Save the channels information to a JSON file.

        Parameters
        ----------
        file_path : path
            The path to the output JSON file.
        """
        with file_path.open(mode="w") as file_stream:
            json.dump(obj=dict(), fp=file_stream, indent=4)
