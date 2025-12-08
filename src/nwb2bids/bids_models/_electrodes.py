import json
import pathlib

import numpy
import pandas
import pydantic
import pynwb
import typing_extensions

from .._inspection._inspection_result import InspectionResult
from ..bids_models._base_metadata_model import BaseMetadataContainerModel, BaseMetadataModel


class Electrode(BaseMetadataModel):
    name: str
    probe_name: str
    hemisphere: str = "N/A"
    x: float = numpy.nan
    y: float = numpy.nan
    z: float = numpy.nan
    impedance: float = numpy.nan  # in kOhms
    shank_id: str = "N/A"
    location: str | None = None

    def __eq__(self, other: typing_extensions.Self) -> bool:
        if not isinstance(other, Electrode):
            raise NotImplementedError

        self_dump = self.model_dump()
        other_dump = other.model_dump()

        if self_dump.keys() != other_dump.keys():
            return False

        for key in self_dump:
            self_val = self_dump[key]
            other_val = other_dump[key]

            # Handle NaN comparison
            if isinstance(self_val, float) and isinstance(other_val, float):
                if numpy.isnan(self_val) and numpy.isnan(other_val):
                    continue

            if self_val != other_val:
                return False

        return True


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
                # material
                location=str(electrode.location.values[0]),
                # TODO: some icephys specific ones (would NOT use the ecephys electrode table anyway...)
                # Probably better off in a designated model
                # pipette_solution=
                # internal_pipette_diameter=
                # external_pipette_diameter=
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

        # Many columns are 'required' by BEP32 but are not always present in the source files or known at all
        required_columns = ["x", "y", "z", "impedance"]
        for column in required_columns:
            data_frame[column] = data_frame[column].fillna(value="N/A")
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
        with file_path.open(mode="w") as file_stream:
            json.dump(obj=dict(), fp=file_stream, indent=4)
