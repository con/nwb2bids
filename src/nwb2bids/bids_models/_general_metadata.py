import json
import pathlib
import typing

import pydantic
import pynwb
import typing_extensions


class GeneralMetadata(pydantic.BaseModel):
    """
    General device and session metadata extracted from NWB files.

    While NWB treats this information as high-level session-specific metadata, BIDS treats these fields as
    modality specific and as pertaining to 'parameters' that can vary.

    This should typically be written to two files, depending on the modality:
      - `_ecephys.json`
      - `_icephys.json`
    """

    InstitutionName: str | None = pydantic.Field(
        description="The name of the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    InstitutionAddress: str | None = pydantic.Field(
        description="The address of the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    InstitutionalDepartmentName: str | None = pydantic.Field(
        description="The department in the institution in charge of the equipment that produced the measurements.",
        default=None,
    )
    PowerLineFrequency: float | typing.Literal["n/a"] = pydantic.Field(
        description=(
            "Frequency (in Hz) of the power grid at the geographical location of the "
            "instrument (for example, 50 or 60)."
        ),
        default="n/a",
    )
    Manufacturer: str | None = pydantic.Field(
        description='Manufacturer of the equipment that produced the measurements. For example, "TDT", "Blackrock".',
        default=None,
    )
    ManufacturersModelName: str | None = pydantic.Field(
        description="Manufacturer's model name of the equipment that produced the measurements.",
        default=None,
    )
    ManufacturersModelVersion: str | None = pydantic.Field(
        description="Manufacturer's model version of the equipment that produced the measurements.",
        default=None,
    )
    RecordingSetupName: str | None = pydantic.Field(
        description="Custom name of the recording setup.",
        default=None,
    )
    SamplingFrequency: float | typing.Literal["n/a"] = pydantic.Field(
        description=(
            "Sampling frequency (in Hz) of all the data in the recording, regardless of their type "
            "(for example, 2400). Internal (maximum) sampling frequency (in Hz) of the recording "
            '(for example, "24000").'
        ),
        default="n/a",
    )
    DeviceSerialNumber: str | None = pydantic.Field(
        description=(
            "The serial number of the equipment that produced the measurements. A pseudonym can also be used to "
            "prevent the equipment from being identifiable, so long as each pseudonym is unique within the dataset. "
            "The serial number of the components of the setup, RECOMMENDED to add serial numbers and versions of ALL "
            "components constituting the setup."
        ),
        default=None,
    )
    SoftwareName: str | None = pydantic.Field(
        description=(
            "Name of the software that was used to present the stimuli. "
            "The name of the software suite used to record the data."
        ),
        default=None,
    )
    SoftwareVersions: str | None = pydantic.Field(
        description="Manufacturer's designation of software version of the equipment that produced the measurements.",
        default=None,
    )
    RecordingDuration: float | None = pydantic.Field(
        description="Length of the recording in seconds (for example, 3600).",
        default=None,
    )
    RecordingType: str | None = pydantic.Field(
        description=(
            'Defines whether the recording is "continuous", "discontinuous", or "epoched", where "epoched" is limited '
            "to time windows about events of interest (for example, stimulus presentations or subject responses). "
            'Must be one of: "continuous", "epoched", "discontinuous".'
        ),
        default=None,
    )
    EpochLength: float | None = pydantic.Field(
        description=(
            "Duration of individual epochs in seconds (for example, 1) in case of epoched data. If recording was "
            "continuous or discontinuous, leave out the field. Must be a number greater than or equal to 0."
        ),
        default=None,
    )
    SoftwareFilters: dict[str, dict[str, typing.Any]] | typing.Literal["n/a"] = pydantic.Field(
        description=(
            'Object of temporal software filters applied, or "n/a" if the data is not available.Each key-value pair '
            "in the JSON object is a name of the filter and an object in which its parameters are defined as "
            "key-value pairs ( for example, "
            '{"Anti-aliasing filter": {"half-amplitude cutoff (Hz)": 500, "Roll-off": "6dB/Octave"}}).'
        ),
        default="n/a",
    )
    HardwareFilters: dict[str, dict[str, typing.Any]] | typing.Literal["n/a"] = pydantic.Field(
        description=(
            'Object of temporal hardware filters applied, or "n/a" if the data is not available. Each key-value pair '
            "in the JSON object is a name of the filter and an object in which its parameters are defined as "
            "key-value pairs. For example, "
            '{"Highpass RC filter": {"Half amplitude cutoff (Hz)": 0.0159, "Roll-off": "6dB/Octave"}}.'
        ),
        default="n/a",
    )
    PharmaceuticalName: str | None = pydantic.Field(
        description="Name of pharmaceutical.",
        default=None,
    )
    PharmaceuticalDoseAmount: float | list[float] | None = pydantic.Field(
        description="Dose amount of administered pharmaceutical.",
        default=None,
    )
    PharmaceuticalDoseUnits: str | None = pydantic.Field(
        description='Unit format relating to pharmaceutical dose (for example, "mg" or "mg/kg").',
        default=None,
    )
    PharmaceuticalDoseRegimen: str | None = pydantic.Field(
        description=(
            "Details of the pharmaceutical dose regimen. Either adequate description or short-code relating to "
            'regimen documented elsewhere (for example, "single oral bolus").'
        ),
        default=None,
    )
    PharmaceuticalDoseTime: float | list[float] | None = pydantic.Field(
        description=(
            "Time of administration of pharmaceutical dose, relative to time zero. For an infusion, this should be a "
            "vector with two elements specifying the start and end of the infusion period. For more complex dose "
            "regimens, the regimen description should be complete enough to enable unambiguous interpretation of "
            '"PharmaceuticalDoseTime". Unit format of the specified pharmaceutical dose time MUST be seconds.'
        ),
        default=None,
    )
    BodyPart: float | None = pydantic.Field(
        description="Body part of the organ / body region scanned.",
        default=None,
    )
    BodyPartDetails: float | None = pydantic.Field(
        description='Additional details about body part or location (for example: "corpus callosum").',
        default=None,
    )
    BodyPartDetailsOntology: float | None = pydantic.Field(
        description=(
            'URI of ontology used for BodyPartDetails (for example: "https://www.ebi.ac.uk/ols/ontologies/uberon").'
        ),
        default=None,
    )
    SampleEnvironment: float | None = pydantic.Field(
        description=(
            'Environment in which the sample was imaged. MUST be one of: "in vivo", "ex vivo" or "in vitro". '
            'Must be one of: "in vivo", "ex vivo", "in vitro".'
        ),
        default=None,
    )
    SampleEmbedding: float | None = pydantic.Field(
        description='Description of the tissue sample embedding (for example: "Epoxy resin").',
        default=None,
    )
    SliceThickness: float | None = pydantic.Field(
        description=(
            'Slice thickness of the tissue sample in the unit micrometers ("um") (for example: 5). '
            "Must be a number greater than 0."
        ),
        default=None,
    )
    SampleExtractionProtocol: float | None = pydantic.Field(
        description="Description of the sample extraction protocol or URI (for example from protocols.io).",
        default=None,
    )
    SupplementarySignals: str | None = pydantic.Field(
        description=(
            "Description of the supplementary signal (additional modalities) recorded in parallel and are "
            "also stored in the data file."
        ),
        default=None,
    )
    TaskName: str | None = pydantic.Field(
        description=(
            "	Name of the task. No two tasks should have the same name. The task label included in the filename "
            'MAY be derived from this "TaskName" field by removing all non-alphanumeric or + characters (that is, '
            "all except those matching [0-9a-zA-Z+]), and potentially replacing spaces with + to ease readability. "
            'For example "TaskName" "faces n-back" or "head nodding" could correspond to task labels faces+n+back '
            "or facesnback and head+nodding or headnodding, respectively. A RECOMMENDED convention is to name "
            "resting state task using labels beginning with rest."
        ),
        default=None,
    )
    TaskDescription: str | None = pydantic.Field(
        description="Longer description of the task.",
        default=None,
    )
    Instructions: str | None = pydantic.Field(
        description=(
            "Text of the instructions given to participants before the recording. This is especially important in "
            "context of resting state recordings and distinguishing between eyes open and eyes closed paradigms."
        ),
        default=None,
    )
    CogAtlasID: str | None = pydantic.Field(
        description="URI of the corresponding Cognitive Atlas Task term.",
        default=None,
    )
    CogPOID: str | None = pydantic.Field(
        description="URI of the corresponding CogPO term.",
        default=None,
    )

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pynwb.NWBFile]) -> typing_extensions.Self:
        """
        Extracts all unique general metadata from the in-memory NWBFile objects.
        """
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        # nwbfile = nwbfiles[0]

        dictionary: dict[str, str] = dict()

        # TODO

        general_metadata = cls(**dictionary)
        return general_metadata

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Save the general metadata to a JSON file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            The path to the file where the metadata will be saved.
        """
        with pathlib.Path(file_path).open(mode="w") as file_stream:
            json.dump(obj=self.model_dump(), fp=file_stream, indent=4)
