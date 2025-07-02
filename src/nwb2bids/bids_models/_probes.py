import json
import pathlib

import pandas
import pydantic
import pynwb
import typing_extensions


class Probe(pydantic.BaseModel):
    probe_id: str
    type: str | None = None
    description: str | None = None
    manufacturer: str | None = None

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )


class ProbeTable(pydantic.BaseModel):
    probes: list[Probe]

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        electrical_series = [
            neurodata_object
            for nwbfile in nwbfiles
            for neurodata_object in nwbfile.objects.values()
            if isinstance(neurodata_object, pynwb.ecephys.ElectricalSeries)
        ]
        if any(electrical_series) is False:
            return None

        unique_devices = {
            electrode_group.device
            for nwbfile in nwbfiles
            for electrode_group in nwbfile.electrodes["group"][:]
            if nwbfile.electrodes is not None
        }

        probes = [
            Probe(
                probe_id=device.name,
                type=None,  # TODO
                description=device.description,
                manufacturer=device.manufacturer,
            )
            for device in unique_devices
        ]
        return cls(probes=probes)

    @pydantic.validate_call
    def to_tsv(self, file_path: str | pathlib.Path) -> None:
        """
        Save the probes information to a TSV file.

        Parameters
        ----------
        file_path : path
            The path to the output TSV file.
        """
        data_frame = pandas.DataFrame(data=[probe.model_dump() for probe in self.probes])
        data_frame.to_csv(path_or_buf=file_path, sep="\t", index=False)

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Save the probes information to a JSON file.

        Parameters
        ----------
        file_path : path
            The path to the output JSON file.
        """
        with file_path.open(mode="w") as file_stream:
            json.dump(obj=dict(), fp=file_stream, indent=4)
