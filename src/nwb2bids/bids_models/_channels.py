import json
import pathlib
import typing

import pandas
import pydantic
import pynwb
import typing_extensions


class Channel(pydantic.BaseModel):
    channel_id: str
    electrode_id: str
    type: typing.Literal["EXT"] = "EXT"  # TODO
    unit: typing.Literal["V"] = "V"
    sampling_frequency: float
    gain: float

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )


class ChannelTable(pydantic.BaseModel):
    channels: list[Channel]

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        nwbfile = nwbfiles[0]

        electrical_series = [
            neurodata_object
            for neurodata_object in nwbfile.objects.values()
            if isinstance(neurodata_object, pynwb.ecephys.ElectricalSeries)
        ]
        if any(electrical_series) is False:
            return None

        channels = [
            Channel(
                channel_id=(
                    str(channel_name.values[0])
                    if (channel_name := electrode.get("channel_name", None)) is not None
                    else str(electrode.index[0])
                ),
                electrode_id=(
                    str(contact_ids.values[0])
                    if (contact_ids := electrode.get("contact_ids", None)) is not None
                    else str(electrode.index[0])
                ),
                type="EXT",
                unit="V",
                sampling_frequency=electrical_series[0].rate,  # TODO: generalize
                gain=electrical_series[0].conversion,
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
        data_frame = pandas.DataFrame(data=[channel.model_dump() for channel in self.channels])
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
