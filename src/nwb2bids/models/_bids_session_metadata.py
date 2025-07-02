import typing

import pydantic
import pynwb


class Subject(pydantic.BaseModel):
    participant_id: str = pydantic.Field(
        description="A unique participant identifier for this subject.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    species: str = pydantic.Field(
        description=(
            "The species should be the proper Latin binomial species name from the NCBI Taxonomy "
            "(for example, Mus musculus)."
        ),
        pattern=r"([A-Z][a-z]* [a-z]+)|(http://purl.obolibrary.org/obo/NCBITaxon_\d+)",  # Latin binomial or NCBI link
        # TODO: see if BIDS validator accepts purl.obolib links directly
    )
    sex: typing.Literal[
        "male", "m", "M", "MALE", "Male", "female", "f", "F", "FEMALE", "Female", "other", "o", "O", "OTHER", "Other"
    ] = pydantic.Field(
        description=(
            'String value indicating phenotypical sex, one of "male", "female", "other".\n'
            '\tFor "male", use one of these values: male, m, M, MALE, Male.\n'
            '\tFor "female", use one of these values: female, f, F, FEMALE, Female.\n'
            '\tFor "other", use one of these values: other, o, O, OTHER, Other.'
        )
    )
    strain: str | None = pydantic.Field(
        description=(
            "For species other than Homo sapiens, the string value indicating the strain of the species "
            "(for example, C57BL/6J)."
        ),
        default=None,
    )


class BidsSessionMetadata(pydantic.BaseModel):
    """
    Schema for the metadata of a single BIDS session.
    """

    session_id: str = pydantic.Field(description="A unique BIDS session identifier.")
    subject: Subject = pydantic.Field(description="Metadata about a subject used in this experiment.")
    extra: dict  # Temporary

    @classmethod
    @pydantic.validate_call
    def from_nwbfile_paths(cls, nwbfile_paths: list[pydantic.FilePath]) -> typing.Self:
        session_metadata: dict = dict()
        for nwb_file_path in nwbfile_paths:
            nwbfile = pynwb.read_nwb(nwb_file_path)

            probes = (
                {electrode_group.device for electrode_group in nwbfile.electrodes["group"][:]}
                if nwbfile.electrodes is not None
                else set()
            )
            electrical_series = [
                neurodata_object
                for neurodata_object in nwbfile.objects.values()
                if isinstance(neurodata_object, pynwb.ecephys.ElectricalSeries)
            ]

            general_metadata = {
                "general_ephys": {
                    "InstitutionName": nwbfile.institution,
                }
            }
            subject_metadata = {
                "subject": {
                    "participant_id": nwbfile.subject.subject_id.replace("_", "-"),
                    "species": nwbfile.subject.species,
                    "strain": nwbfile.subject.strain,
                    # "birthday": nwbfile.subject.date_of_birth, # TODO
                    # "age": nwbfile.subject.age,
                    "sex": nwbfile.subject.sex,
                }
            }
            session_metadata = {
                "session": {
                    "session_id": nwbfile.session_id,
                    "number_of_trials": len(nwbfile.trials) if nwbfile.trials else None,
                    "comments": nwbfile.session_description,
                }
            }
            probe_metadata = {
                "probes": [
                    {
                        "probe_id": probe.name,
                        "type": "unknown",
                        "description": probe.description,
                        "manufacturer": probe.manufacturer,
                    }
                    for probe in probes
                ]
            }
            electrode_metadata = (
                {
                    "electrodes": [
                        {
                            "electrode_id": electrode.index[0],
                            "probe_id": electrode.group.iloc[0].device.name,
                            # TODO "impedance": electrode["imp"].iloc[0] if electrode["imp"].iloc[0] > 0 else None,
                            "location": (
                                electrode["location"].iloc[0]
                                if electrode["location"].iloc[0] not in ("unknown",)
                                else None
                            ),
                        }
                        for electrode in nwbfile.electrodes
                    ]
                }
                if nwbfile.electrodes is not None
                else dict()
            )
            channels_metadata = (
                {
                    "channels": [
                        {
                            "channel_id": electrode.index[0],
                            "electrode_id": electrode.index[0],
                            "type": "EXT",
                            "unit": "V",
                            "sampling_frequency": electrical_series[0].rate,  # TODO: generalize
                            "gain": electrical_series[0].conversion,
                        }
                        for electrode in nwbfile.electrodes
                    ]
                }
                if nwbfile.electrodes is not None
                else dict()
            )
            session_metadata.update(
                **general_metadata,
                **subject_metadata,
                **session_metadata,
                **probe_metadata,
                **electrode_metadata,
                **channels_metadata,
            )

        session_id = session_metadata["session"]["session_id"]
        subject = Subject(**session_metadata["subject"])
        return cls(session_id=session_id, subject=subject, extra=session_metadata)
