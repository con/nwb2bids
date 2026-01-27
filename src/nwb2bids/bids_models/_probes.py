import collections
import json
import pathlib
import typing
from typing import Any

import pandas
import pydantic
import pynwb
import typing_extensions

from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel
from ..notifications import Notification


class Probe(BaseMetadataModel):
    probe_name: str = pydantic.Field(
        description="A unique identifier of the probe, can be identical with the device_serial_number.",
        title="Probe name",
    )
    type: str = pydantic.Field(description="The type of the probe.", title="Type", default="n/a")
    AP: float | None = pydantic.Field(
        description=(
            "Probe position along the Anterior-Posterior axis. Positive values are anterior to the reference point."
        ),
        title="AP",
        default=None,
    )
    ML: float | None = pydantic.Field(
        description=(
            "Probe position along the Medial-Lateral axis. Positive values are to the right (as seen from behind)."
        ),
        title="ML",
        default=None,
    )
    DV: float | None = pydantic.Field(
        description="Probe position along the Dorsal-Ventral axis. Positive values are ventral.",
        title="DV",
        default=None,
    )
    AP_angle: float | None = pydantic.Field(
        description=(
            "Anterior-Posterior rotation angle measured as rotation from the vertical axis in the sagittal plane. "
            "0° represents vertical along DV axis. Positive values indicate anterior rotation."
        ),
        title="AP angle",
        default=None,
    )
    ML_angle: float | None = pydantic.Field(
        description=(
            "Medial-Lateral rotation angle measured as rotation from the vertical axis in the coronal plane. "
            "0° represents vertical along DV axis. Positive values indicate rightward/clockwise rotation "
            "(as seen from behind)."
        ),
        title="ML angle",
        default=None,
    )
    manufacturer: str | None = pydantic.Field(
        description="Manufacturer of the probes system (for example, 'openephys', 'alphaomega','blackrock').",
        title="Manufacturer",
        default=None,
    )
    model: str | None = pydantic.Field(
        description="The model name or number of the probe (for example, Neuropixels 1.0, A1x32-Poly3-5mm-25s-177).",
        title="Model",
        default=None,
    )
    device_serial_number: str | None = pydantic.Field(
        description="The serial number of the probe (provided by the manufacturer).",
        title="Device serial number",
        default=None,
    )
    electrode_count: int | None = pydantic.Field(
        description="Number of miscellaneous analog electrodes for auxiliary signals (for example, '2').",
        title="Electrode count",
        default=None,
    )
    width: float | None = pydantic.Field(
        description=(
            "Physical width of the probe in mm, for example, '5'. "
            "This dimension corresponds to the x-axis of the probe's local coordinate frame."
        ),
        title="Width",
        default=None,
    )
    height: float | None = pydantic.Field(
        description=(
            "Physical height of the probe in mm, for example, '0.3'. "
            "This dimension should be omitted or set to 0 for one-dimensional (linear) probes. "
            "This dimension corresponds to the y-axis of the probe's local coordinate frame."
        ),
        title="Height",
        default=None,
    )
    depth: float | None = pydantic.Field(
        description=(
            "Physical depth of the probe in mm, for example, '0.3'. "
            "This dimension should be omitted or set to 0 for two-dimensional (shank-type) probes. "
            "This dimension corresponds to the z-axis of the probe's local coordinate frame."
        ),
        title="Depth",
        default=None,
    )
    rotation_angle: float | None = pydantic.Field(
        description=(
            "Rotation angle around the probe axis. "
            "0° when probe features align with the coronal plane. "
            "Positive rotation is clockwise when viewed from above."
        ),
        title="Rotation angle",
        default=None,
    )
    coordinate_reference_point: str | None = pydantic.Field(
        description=(
            "Point of the probe that is described by the probe coordinates and on which the yaw, pitch, "
            "and roll rotations are applied."
        ),
        title="Coordinate reference point",
        default=None,
    )
    anatomical_reference_point: str | None = pydantic.Field(
        description=(
            "Anatomical reference point for stereotaxic coordinates (for example, Bregma, Lambda). "
            "If not specified, Bregma is assumed for rodents. MUST be defined for species other than rodents."
        ),
        title="Anatomical reference point",
        default=None,
    )
    hemisphere: typing.Literal["L", "R"] | None = pydantic.Field(
        description="Hemisphere in which the probe is placed.", title="Hemisphere", default=None
    )
    associated_brain_region: str | None = pydantic.Field(
        description=(
            "A textual indication on the location of the probe, preferably species-independent terms as obtained, "
            "for example from Uberon."
        ),
        title="Associated brain region",
        default=None,
    )
    associated_brain_region_id: str | None = pydantic.Field(
        description=(
            "An identifier of the associated brain region based on the Uberon ontology for anatomical structures "
            'in animals, for example "UBERON:0010415"'
        ),
        title="Associated brain region ID",
        default=None,
    )
    associated_brain_region_quality_type: str | None = pydantic.Field(
        description="The method used to identify the associated brain region (estimated).",
        title="Associated brain region quality type",
        default=None,
    )
    reference_atlas: str | None = pydantic.Field(
        description=(
            "Name of reference atlas used for associated brain region identification, "
            "preferably an ebrains supported atlas."
        ),
        title="Reference atlas",
        default=None,
    )
    material: str | None = pydantic.Field(
        description="A textual description of the base material of the probe.", title="Material", default=None
    )


class ProbeTable(BaseMetadataContainerModel):
    probes: list[Probe]
    modality: typing.Literal["ecephys", "icephys"]

    def _check_fields(self) -> None:
        self._internal_notifications = []

        probes_missing_description = [probe for probe in self.probes if probe.description is None]
        for _ in probes_missing_description:
            notification = Notification.from_definition(
                identifier="MissingDescription",
                source_file_paths=[],  # TODO: figure out better way of handling here
                # field=f"nwbfile.devices.{probe_missing_description.probe_name}",  # TODO: improve field handling
            )
            self._internal_notifications.append(notification)

    def model_post_init(self, context: Any, /) -> None:
        self._check_fields()

        self._non_defaulted_probe_fields = {
            field
            for probe in self.probes
            for field, value in probe.model_dump().items()
            if value is not None and field != getattr(probe.model_fields.get(field, []), "default", None) is not None
        }

    @pydantic.computed_field
    @property
    def notifications(self) -> list[Notification]:
        """
        All notifications from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        notifications = [notification for probe in self.probes for notification in probe.notifications]
        notifications += self._internal_notifications
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

        has_ecephys_probes = nwbfile.electrodes is not None
        has_icephys_probes = any(nwbfile.icephys_electrodes)
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
                type="n/a",  # TODO via additional metadata
                manufacturer=device.manufacturer,
                description=device.description,
                # TODO: handle more extra custom columns
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

        probe_fields = Probe.model_fields
        default_descriptions = {
            "description": {"Description": "Probe description from NWB file.", "LongName": "Description"}
        }

        json_content: dict[str, dict[str, Any]] = collections.defaultdict(dict)
        for field in self._non_defaulted_probe_fields:
            if title := getattr(probe_fields[field], "title"):
                json_content[field]["LongName"] = title
            if description := getattr(probe_fields[field], "description"):
                json_content[field]["Description"] = description
        json_content.update(default_descriptions)

        if "hemisphere" in json_content:
            json_content["hemisphere"]["Levels"] = {"L": "left", "R": "right"}

        with file_path.open(mode="w") as file_stream:
            json.dump(obj=json_content, fp=file_stream, indent=4)
