import json
import pathlib

import pandas
import pydantic
import pynwb
import typing_extensions

from .._inspection._inspection_result import InspectionResult
from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel


class Electrode(BaseMetadataModel):
    electrode_id: int
    probe_id: str
    location: str | None = None


class ElectrodeTable(BaseMetadataContainerModel):
    electrodes: list[Electrode]

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        messages = [message for electrode in self.electrodes for message in electrode.messages]
        messages.sort(key=lambda message: (-message.category.value, -message.severity.value, message.title))
        return messages

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

        electrodes = [
            Electrode(
                electrode_id=electrode.index[0],
                probe_id=electrode.group.iloc[0].device.name,
                # TODO "impedance": electrode["imp"].iloc[0] if electrode["imp"].iloc[0] > 0 else None,
                location=str(electrode.location.values[0]),
            )
            for electrode in nwbfile.electrodes
        ]
        return cls(electrodes=electrodes)

    @pydantic.validate_call
    def to_tsv(self, file_path: str | pathlib.Path) -> None:
        """
        Write the electrode data to a TSV file.

        Parameters
        ----------
        file_path : path
            The path to the output TSV file.
        """
        data = []
        for electrode in self.electrodes:
            model_dump = electrode.model_dump()
            data.append(model_dump)

        data_frame = pandas.DataFrame(data=data)
        data_frame.to_csv(file_path, sep="\t", index=False)

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Save the electrode information to a JSON file.

        Parameters
        ----------
        file_path : path
            The path to the output JSON file.
        """
        with file_path.open(mode="w") as file_stream:
            json.dump(obj=dict(), fp=file_stream, indent=4)
