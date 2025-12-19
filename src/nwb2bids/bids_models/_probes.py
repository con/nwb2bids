import json
import pathlib
from typing import Any

import pandas
import pydantic
import pynwb
import typing_extensions

from .._inspection._inspection_result import Category, DataStandard, InspectionResult, Severity
from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel


class Probe(BaseMetadataModel):
    probe_name: str
    type: str | None = None
    description: str | None = None
    manufacturer: str | None = None


class ProbeTable(BaseMetadataContainerModel):
    probes: list[Probe]

    def _check_fields(self) -> None:
        # Check if values are specified
        self._internal_messages = []

        probes_missing_description = [probe for probe in self.probes if probe.description is None]
        for probe_missing_description in probes_missing_description:
            self._internal_messages.append(
                InspectionResult(
                    title="Missing description",
                    reason="A basic description of this field is recommended to improve contextual understanding.",
                    solution="Add a description to the field.",
                    field=f"nwbfile.devices.{probe_missing_description.probe_name}",
                    source_file_paths=[],  # TODO: figure out better way of handling
                    data_standards=[DataStandard.BIDS, DataStandard.NWB],
                    category=Category.STYLE_SUGGESTION,
                    severity=Severity.INFO,
                )
            )

    def model_post_init(self, context: Any, /) -> None:
        self._check_fields()

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        messages = [message for probe in self.probes for message in probe.messages]
        messages += self._internal_messages
        messages.sort(key=lambda message: (-message.category.value, -message.severity.value, message.title))
        return messages

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        nwb_electrode_tables = [nwbfile.electrodes for nwbfile in nwbfiles]
        if not any(nwb_electrode_tables):
            return None

        unique_devices = {
            electrode_group.device
            for nwbfile in nwbfiles
            for electrode_group in nwbfile.electrodes["group"][:]
            if nwbfile.electrodes is not None
        }

        probes = [
            Probe(
                probe_name=device.name,
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
        data = []
        for probe in self.probes:
            model_dump = probe.model_dump()
            data.append(model_dump)

        data_frame = pandas.DataFrame(data=data)
        data_frame["type"] = data_frame["type"].fillna(value="N/A")
        data_frame = data_frame.dropna(axis=1, how="all")
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
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)

        with file_path.open(mode="w") as file_stream:
            json.dump(obj=dict(), fp=file_stream, indent=4)
