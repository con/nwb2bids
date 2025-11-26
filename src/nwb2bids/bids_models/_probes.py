import json
import pathlib

import pandas
import pydantic
import pynwb
import typing_extensions

from .._inspection._inspection_result import Category, DataStandard, InspectionResult, Severity
from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel


class Probe(BaseMetadataModel):
    probe_id: str
    type: str | None = None
    description: str | None = None
    manufacturer: str | None = None


class ProbeTable(BaseMetadataContainerModel):
    probes: list[Probe]

    def _check_fields(self, file_paths: list[pathlib.Path] | list[pydantic.HttpUrl]) -> None:
        # Check if values are specified
        probes_missing_description = [probe for probe in self.probes if probe.description is None]
        for probe_missing_description in probes_missing_description:
            self.messages.append(
                InspectionResult(
                    title="Missing description",
                    reason="A basic description of this field is recommended to improve contextual understanding.",
                    solution="Add a description to the field.",
                    field=f"nwbfile.devices.{probe_missing_description.probe_id}",
                    source_file_paths=file_paths,
                    data_standards=[DataStandard.BIDS, DataStandard.NWB],
                    category=Category.STYLE_SUGGESTION,
                    severity=Severity.INFO,
                )
            )

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        messages = [message for probe in self.probes for message in probe.messages]
        messages.sort(key=lambda message: (-message.category.value, -message.severity.value, message.title))
        return messages

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        file_paths = [nwbfile.container_source for nwbfile in nwbfiles]

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
        probes._check_fields(file_paths=file_paths)
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
        data = []
        for probe in self.probes:
            model_dump = probe.model_dump()
            data.append(model_dump)

        data_frame = pandas.DataFrame(data=data)
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
