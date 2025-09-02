import json
import pathlib

import numpy
import pydantic
import pynwb
import typing_extensions


class EphysMetadata(pydantic.BaseModel):
    """
    General device and session metadata extracted from NWB files.

    While NWB treats this information as high-level session-specific metadata, BIDS treats these fields as
    modality specific and as pertaining to 'parameters' that can vary.
    """

    InstitutionName: str = pydantic.Field(
        description="The name of the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    InstitutionAddress: str = pydantic.Field(
        description="The address of the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    InstitutionalDepartmentName: str = pydantic.Field(
        description="The department in the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    PowerLineFrequency: float = pydantic.Field(
        description=(
            "Frequency (in Hz) of the power grid at the geographical location of the instrument "
            "(for example, 50 or 60)."
        ),
        default=60,  # TODO: appeal requirement for this
    )
    Manufacturer: str = pydantic.Field(
        description=('Manufacturer of the equipment that produced the measurements. For example, "TDT", "Blackrock".'),
        default=None,
    )
    ManufacturersModelName: str = pydantic.Field(
        description="Manufacturer's model name of the equipment that produced the measurements.",
        default=None,
    )
    ManufacturersModelVersion: str = pydantic.Field(
        description="Manufacturer's model version of the equipment that produced the measurements.",
        default=None,
    )
    RecordingSetupName: str = pydantic.Field(
        description="Custom name of the recording setup.",
        default=None,
    )
    SamplingFrequency: float = pydantic.Field(
        description=(
            "Sampling frequency (in Hz) of all the data in the recording, regardless of their type (for example, "
            '2400). Internal (maximum) sampling frequency (in Hz) of the recording (for example, "24000").'
        ),
    )
    DeviceSerialNumber: str = pydantic.Field(
        description=(
            "The serial number of the equipment that produced the measurements. "
            "A pseudonym can also be used to prevent the equipment from being identifiable, so long as each pseudonym "
            "is unique within the dataset. The serial number of the components of the setup, "
            "RECOMMENDED to add serial numbers and versions of ALL components constituting the setup."
        ),
        default=None,
    )
    SoftwareName: str = pydantic.Field(
        description=(
            "Name of the software that was used to present the stimuli. "
            "The name of the software suite used to record the data."
        ),
        default=None,
    )
    SoftwareVersions: str = pydantic.Field(
        description="Manufacturer's designation of software version of the equipment that produced the measurements.",
        default=None,
    )

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        """
        Extracts all unique general metadata from the in-memory NWBFile objects.
        """
        institution_names = {nwbfile.institution for nwbfile in nwbfiles} - {None}
        manufacturers = {device.manufacturer for nwbfile in nwbfiles for device in nwbfile.devices} - {None}
        sampling_frequencies = {
            time_series.rate
            for nwbfile in nwbfiles
            for time_series in nwbfile.objects.values()
            if isinstance(time_series, pynwb.TimeSeries)
        } - {None}

        # Use timestamps diff as a fallback if no sampling frequencies are found
        if len(sampling_frequencies) == 0:
            all_timestamp_diffs = [
                numpy.mean(numpy.diff(time_series.timestamps))
                for nwbfile in nwbfiles
                for time_series in nwbfile.objects.values()
                if isinstance(time_series, pynwb.TimeSeries)
            ]

        institution_name_string = "; ".join(institution_names) if len(institution_names) > 0 else None
        manufacturer_string = "; ".join(manufacturers) if len(manufacturers) > 0 else None
        sampling_frequency_string = (
            list(sampling_frequencies)[:1] if len(sampling_frequencies) > 0 else all_timestamp_diffs[:1]
        )

        ephys_metadata = cls(
            InstitutionName=institution_name_string,
            Manufacturer=manufacturer_string,
            SamplingFrequency=sampling_frequency_string,
        )
        return ephys_metadata

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Write the BIDS general ephys metadata JSON sidecar file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            The path to the output JSON file.
        """
        with file_path.open(mode="w") as file_stream:
            json.dump(obj=self.model_dump_json(), fp=file_stream, indent=4)
