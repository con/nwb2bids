import json
import pathlib
import typing
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
    manufacturer: str | None = None


class ProbeTable(BaseMetadataContainerModel):
    probes: list[Probe]
    modality: typing.Literal["ecephys", "icephys"]

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
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        nwbfile = nwbfiles[0]

        has_ecephys_probes = nwbfile.electrodes is not None
        has_icephys_probes = nwbfile.icephys_electrodes is not None
        if not has_ecephys_probes and not has_icephys_probes:
            return None

        if has_ecephys_probes and has_icephys_probes:
            message = (
                "Converting probe metadata when there are both ecephys and icephys types has not yet been implemented."
            )
            raise NotImplementedError(message)

        modality = "ecephys" if has_ecephys_probes else "icephys"
        if modality == "ecephys":
            electrode_groups = nwbfile.electrodes["group"][:]
            unique_devices = {electrode_group.device for electrode_group in electrode_groups}
        else:
            icephys_electrodes = nwbfile.icephys_electrodes.values()
            unique_devices = {electrode.device for electrode in icephys_electrodes}

        probes = [
            Probe(
                probe_name=device.name,
                type=None,  # TODO
                manufacturer=device.manufacturer,
                # TODO: handle extra custom columns like description
                # description=device.description,
            )
            for device in unique_devices
        ]
        return cls(probes=probes, modality=modality)

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
        file_path = pathlib.Path(file_path)

        with file_path.open(mode="w") as file_stream:
            json.dump(
                obj=dict(),  # TODO
                fp=file_stream,
                indent=4,
            )
