import json
import pathlib
import typing

import numpy
import pandas
import pydantic
import pynwb
import typing_extensions

from ._model_utils import _build_json_sidecar
from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel
from ..notifications import Notification

_NULL_LOCATION_PLACEHOLDERS = {"", "unknown", "no location", "N/A"}


class Electrode(BaseMetadataModel):
    name: str = pydantic.Field(
        description="Name of the electrode contact point.",
        title="Electrode name",
    )
    probe_name: str = pydantic.Field(
        description=(
            "A unique identifier of the probe, can be identical with the device_serial_number. "
            "The value MUST match a probe_name entry in the corresponding *_probes.tsv file, linking this electrode "
            "to its associated probe. For electrodes not associated with a probe, use n/a."
        ),
        title="Probe name",
    )
    x: float = pydantic.Field(
        description=(
            "Recorded position along the x-axis. When no space-<label> entity is used in the filename, "
            "the position along the local width-axis relative to the probe origin "
            "(see coordinate_reference_point in *_probes.tsv) in micrometers (um). "
            "When a space-<label> entity is used in the filename, the position relative to the origin of the "
            "coordinate system along the first axis. Units are specified by MicroephysCoordinateUnits in the "
            "corresponding *_coordsystem.json file."
        ),
        title="x",
        default=numpy.nan,
    )
    y: float = pydantic.Field(
        description=(
            "Recorded position along the y-axis. When no space-<label> entity is used in the filename, "
            "the position along the local height-axis relative to the probe origin "
            "(see coordinate_reference_point in *_probes.tsv) in micrometers (um). "
            "When a space-<label> entity is used in the filename, the position relative to the origin of the "
            "coordinate system along the second axis. Units are specified by MicroephysCoordinateUnits in the "
            "corresponding *_coordsystem.json file."
        ),
        title="y",
        default=numpy.nan,
    )
    z: float = pydantic.Field(
        description=(
            "Recorded position along the z-axis. For 2D electrode localizations, "
            "this SHOULD be a column of n/a values. "
            "When no space-<label> entity is used in the filename, the position along the local depth-axis relative to "
            "the probe origin (see coordinate_reference_point in *_probes.tsv) in micrometers (um). "
            "When a space-<label> entity is used in the filename, the position relative to the origin of the "
            "coordinate system along the third axis. Units are specified by MicroephysCoordinateUnits in the "
            "corresponding *_coordsystem.json file. For 2D electrode localizations (for example, when the "
            "coordinate system is Pixels), this SHOULD be a column of n/a values."
        ),
        title="z",
        default=numpy.nan,
    )
    hemisphere: typing.Literal["L", "R", "n/a"] = pydantic.Field(
        description="The hemisphere in which the electrode is placed.", title="Hemisphere", default="n/a"
    )
    impedance: float = pydantic.Field(
        description="Impedance of the electrode, units MUST be in kOhm.", title="Impedance", default=numpy.nan
    )
    shank_id: str = pydantic.Field(
        description=(
            "A unique identifier to specify which shank of the probe the electrode is on. "
            "This is useful for spike sorting when the electrodes are on a multi-shank probe."
        ),
        title="Shank ID",
        default="n/a",
    )
    size: float | None = pydantic.Field(
        description="Surface area of the electrode, units MUST be in um^2.",
        title="Size",
        default=None,
    )
    electrode_shape: str | None = pydantic.Field(
        description="Description of the shape of the electrode (for example, square, circle).",
        title="Electrode shape",
        default=None,
    )
    material: str | None = pydantic.Field(
        description="Material of the electrode (for example, Tin, Ag/AgCl, Gold).",
        title="Material",
        default=None,
    )
    location: str | None = pydantic.Field(
        description="An indication on the location of the electrode (for example, cortical layer 3, CA1).",
        title="Location",
        default=None,
    )
    pipette_solution: str | None = pydantic.Field(
        description="The solution used to fill the pipette.",
        title="Pipette solution",
        default=None,
    )
    internal_pipette_diameter: float | None = pydantic.Field(
        description="The internal diameter of the pipette in micrometers.",
        title="Internal pipette diameter",
        default=None,
    )
    external_pipette_diameter: float | None = pydantic.Field(
        description="The external diameter of the pipette in micrometers.",
        title="External pipette diameter",
        default=None,
    )

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, Electrode):
            return False

        self_dump = self.model_dump()
        other_dump = other.model_dump()

        if self_dump.keys() != other_dump.keys():
            return False

        for key in self_dump:
            self_val = self_dump[key]
            other_val = other_dump[key]

            # Handle NaN comparison (NaN == NaN should be true)
            if isinstance(self_val, float) and isinstance(other_val, float):
                if numpy.isnan(self_val) and numpy.isnan(other_val):
                    continue

            if self_val != other_val:
                return False

        return True


class ElectrodeTable(BaseMetadataContainerModel):
    electrodes: list[Electrode]
    modality: typing.Literal["ecephys", "icephys"]

    @pydantic.computed_field
    @property
    def notifications(self) -> list[Notification]:
        """
        All notifications from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        notifications = [notification for electrode in self.electrodes for notification in electrode.notifications]
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
            electrodes = [
                Electrode(
                    # Leading 'e' and padding are by convention from BEP32 examples
                    name=f"e{str(electrode.index[0]).zfill(3)}",
                    probe_name=electrode.group.iloc[0].device.name,
                    # TODO: hemisphere determination from additional metadata or possible lookup from a location map
                    x=electrode.x.iloc[0] if "x" in electrode else numpy.nan,
                    y=electrode.y.iloc[0] if "y" in electrode else numpy.nan,
                    z=electrode.z.iloc[0] if "z" in electrode else numpy.nan,
                    # Impedance must be in kOhms for BEP32 but NWB specifies Ohms
                    impedance=(
                        eimp_in_ohms / 1e3
                        if "imp" in electrode and not pandas.isna(eimp_in_ohms := electrode.imp.iloc[0])
                        else numpy.nan
                    ),
                    shank_id=electrode.group.iloc[0].name,
                    # TODO: pretty much only through additional metadata
                    # size=
                    # electrode_shape=
                    # material=
                    location=(
                        "n/a" if (val := str(electrode.location.values[0])) in _NULL_LOCATION_PLACEHOLDERS else val
                    ),
                    # TODO: add extra columns
                )
                for electrode in nwbfile.electrodes
            ]
        else:
            electrodes = [
                Electrode(
                    name=electrode.name,
                    probe_name=electrode.device.name,
                    # TODO: hemisphere, location, impedance may all have to be specified through custom columns
                    x=getattr(electrode, "x", numpy.nan),
                    y=getattr(electrode, "y", numpy.nan),
                    z=getattr(electrode, "z", numpy.nan),
                    # TODO: pretty much only through additional metadata
                    # impedance=
                    # size=
                    # electrode_shape=
                    # material=
                    location=getattr(electrode, "location", None),
                    # TODO: some icephys specific ones (would NOT use the ecephys electrode table anyway...)
                    # pipette_solution=
                    # internal_pipette_diameter=
                    # external_pipette_diameter=
                    # TODO: add extra columns
                )
                for electrode in nwbfile.icephys_electrodes.values()
            ]
        return cls(electrodes=electrodes, modality=modality)

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

        # Many columns are 'required' by BEP32 but are not always present in the source files or known at all
        required_columns = ["x", "y", "z", "impedance"]
        for column in required_columns:
            data_frame[column] = data_frame[column].fillna(value="n/a")
        data_frame = data_frame.dropna(axis=1, how="all")
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
        file_path = pathlib.Path(file_path)

        json_content = _build_json_sidecar(models=self.electrodes)

        if "hemisphere" in json_content:
            json_content["hemisphere"]["Levels"] = {"L": "left", "R": "right"}

        with file_path.open(mode="w") as file_stream:
            json.dump(obj=json_content, fp=file_stream, indent=4)
