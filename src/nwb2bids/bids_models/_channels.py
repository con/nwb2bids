import collections
import json
import pathlib
import typing
import warnings

import pandas
import pydantic
import pynwb
import typing_extensions

from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel
from ..notifications import Notification


def _infer_scalar_field(
    electrode_name_to_series: dict[str, list[pynwb.icephys.PatchClampSeries]], field_name: str
) -> dict[str, float | None]:
    """For icephys specifically, infer some scalar field (e.g., rate, gain) for each electrode name."""
    electrode_name_to_field_values = collections.defaultdict(set)
    for electrode_name, series_list in electrode_name_to_series.items():
        for series in series_list:
            field_value = getattr(series, field_name, None)
            if field_value is not None:
                electrode_name_to_field_values[electrode_name].add(field_value)

    electrode_name_to_field = dict()
    for electrode_name, field_values in electrode_name_to_field_values.items():
        if len(ls := list(field_values)) == 1:
            electrode_name_to_field[electrode_name] = ls[0]
        else:
            message = (
                f"Some PatchClampSeries associated with electrode {electrode_name} have conflicting "
                f"{field_name}s: {field_values}. Automatic detection of channel {field_name} for this "
                "case is not yet implemented."
            )
            warnings.warn(message=message, stacklevel=2)

    return electrode_name_to_field


class Channel(BaseMetadataModel):
    channel_name: str
    reference: str
    type: str = "N/A"
    unit: str = "V"
    sampling_frequency: float | None = None
    channel_label: str | None = None
    stream_id: str | None = None
    description: str | None = None
    status: typing.Literal["good", "bad"] | None = None
    status_description: str | None = None
    gain: float | None = None
    time_offset: float | None = None
    time_reference_channels: str | None = None
    ground: str | None = None
    # recording_mode: str | None = None  # TODO: icephys only


class ChannelTable(BaseMetadataContainerModel):
    channels: list[Channel]
    modality: typing.Literal["ecephys", "icephys"]

    @pydantic.computed_field
    @property
    def notifications(self) -> list[Notification]:
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

        has_ecephys_electrodes = nwbfile.electrodes is not None
        has_icephys_electrodes = any(nwbfile.icephys_electrodes)
        if not has_ecephys_electrodes and not has_icephys_electrodes:
            return None

        if has_ecephys_electrodes and has_icephys_electrodes:
            message = (
                "Converting electrode metadata when there are both ecephys and icephys types "
                "has not yet been implemented."
            )
            raise NotImplementedError(message)

        modality = "ecephys" if has_ecephys_electrodes else "icephys"
        if modality == "ecephys":
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
        else:
            icephys_series = [
                neurodata_object
                for neurodata_object in nwbfile.acquisition.values()
                if isinstance(neurodata_object, pynwb.icephys.PatchClampSeries)
            ]
            # TODO: handle intracellular_recordings case
            electrode_name_to_series = collections.defaultdict(list)
            for series in icephys_series:
                electrode_name_to_series[series.electrode.name].append(series)

            electrode_name_to_sampling_frequency = _infer_scalar_field(
                electrode_name_to_series=electrode_name_to_series, field_name="rate"
            )
            electrode_name_to_gain = _infer_scalar_field(
                electrode_name_to_series=electrode_name_to_series, field_name="gain"
            )
            electrode_name_to_class = _infer_scalar_field(
                electrode_name_to_series=electrode_name_to_series, field_name="__class__"
            )

            class_name_to_type = {
                "VoltageClampSeries": "VM",
                "CurrentClampSeries": "IM",
            }
            electrode_name_to_type = {
                electrode_name: class_name_to_type.get(series_class.__name__, "n/a")
                for electrode_name, series_class in electrode_name_to_class.items()
            }
            type_to_recording_mode = {
                "VM": "voltage-clamp",
                "IM": "current-clamp",
                "n/a": "n/a",
            }

            electrode_name_to_stream_ids = {
                electrode_name: ",".join([series.name for series in series_list])
                for electrode_name, series_list in electrode_name_to_series.items()
            }

            channels = [
                Channel(
                    channel_name=electrode.name,
                    reference="n/a",  # TODO: think about if/how this could be any other value
                    type=electrode_name_to_type.get(electrode.name, "n/a"),
                    unit="V",
                    sampling_frequency=electrode_name_to_sampling_frequency.get(electrode.name, None),
                    # channel_label: str | None = None # TODO: only support with additional metadata
                    stream_id=electrode_name_to_stream_ids.get(electrode.name, None),
                    # description: str | None = None  # TODO: only support with additional metadata
                    # status: typing.Literal["good", "bad"] | None = None # TODO: only support with additional metadata
                    # status_description: str | None = None # TODO: only support with additional metadata
                    gain=electrode_name_to_gain.get(electrode.name, None),
                    # time_offset=
                    # time_reference_channels: str | None = None # TODO: only support with additional metadata
                    # ground: str | None = None # TODO: only support with additional metadata
                    recording_mode=type_to_recording_mode[electrode_name_to_type.get(electrode.name, "n/a")],
                    # TODO: add extra columns
                )
                for electrode in nwbfile.icephys_electrodes.values()
            ]
        return cls(channels=channels, modality=modality)

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
            json.dump(
                obj=dict(),  # TODO
                fp=file_stream,
                indent=4,
            )
