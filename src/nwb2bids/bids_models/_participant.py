import re
import typing
import warnings

import pydantic
import pynwb
import typing_extensions

_SPECIES_REGEX = r"([A-Z][a-z]* [a-z]+)|(http://purl.obolibrary.org/obo/NCBITaxon_\d+)"


class Participant(pydantic.BaseModel):
    participant_id: str = pydantic.Field(
        description="A unique identifier for this participant.",
        pattern=r"^[^_]+$",  # No underscores allowed
    )
    species: str | None = pydantic.Field(
        description=(
            "The species should be the proper Latin binomial species name from the NCBI Taxonomy "
            "(for example, Mus musculus)."
        ),
        pattern=_SPECIES_REGEX,
        default=None,
    )
    sex: (
        typing.Literal[
            "male",
            "m",
            "M",
            "MALE",
            "Male",
            "female",
            "f",
            "F",
            "FEMALE",
            "Female",
            "other",
            "o",
            "O",
            "OTHER",
            "Other",
        ]
        | None
    ) = pydantic.Field(
        description=(
            'String value indicating phenotypical sex, one of "male", "female", "other".\n'
            '\tFor "male", use one of these values: male, m, M, MALE, Male.\n'
            '\tFor "female", use one of these values: female, f, F, FEMALE, Female.\n'
            '\tFor "other", use one of these values: other, o, O, OTHER, Other.'
        ),
        default=None,
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
        participant_id = nwbfile.subject.subject_id.replace("_", "-")

        species = nwbfile.subject.species
        if species is not None and not re.match(pattern=_SPECIES_REGEX, string=species):
            message = (
                f"Subject species '{species}' within NWB file is not a proper Latin binomial or NCBI Taxonomy link. "
                "Skipping automated extraction."
            )
            warnings.warn(message=message, stacklevel=2)
            species = None

        sex = nwbfile.subject.sex
        if nwbfile.subject.sex is not None and nwbfile.subject.sex not in [
            "male",
            "m",
            "M",
            "MALE",
            "Male",
            "female",
            "f",
            "F",
            "FEMALE",
            "Female",
            "other",
            "o",
            "O",
            "OTHER",
            "Other",
        ]:
            message = (
                f"Subject sex '{sex}' within NWB file is not one of the allowed patterns. "
                "Skipping automated extraction."
            )
            warnings.warn(message=message, stacklevel=2)
            sex = None

        subject = cls(
            participant_id=participant_id,
            species=species,
            sex=sex,
            strain=nwbfile.subject.strain,
            # TODO: add more
            # birthday=nwbfile.participant.date_of_birth,
            # age=nwbfile.participant.age
        )
        return subject
