import typing

import pydantic
import pynwb
import typing_extensions


class Participant(pydantic.BaseModel):
    participant_id: str = pydantic.Field(
        description="A unique identifier for this participant.",
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

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self:
        """
        Extracts participant metadata from the in-memory NWBFile objects.
        """
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)

        nwbfile = nwbfiles[0]

        subject = cls(
            participant_id=nwbfile.subject.subject_id.replace("_", "-"),
            species=nwbfile.subject.species,
            strain=nwbfile.subject.strain,
            sex=nwbfile.subject.sex,
            # TODO: add more
            # birthday=nwbfile.participant.date_of_birth,
            # age=nwbfile.participant.age
        )
        return subject
