import pathlib
import re

import pydantic
import pynwb
import typing_extensions

from ._model_globals import _VALID_ARCHIVES_SEXES, _VALID_BIDS_SEXES, _VALID_PARTICIPANT_ID_REGEX, _VALID_SPECIES_REGEX
from .._messages._inspection_message import InspectionLevel, InspectionMessage
from ..bids_models._base_metadata_model import BaseMetadataModel


class Participant(BaseMetadataModel):
    participant_id: str = pydantic.Field(
        description="A unique identifier for this participant.",
        default=None,
    )
    species: str | None = pydantic.Field(
        description=(
            "The species should be the proper Latin binomial species name from the NCBI Taxonomy "
            "(for example, Mus musculus)."
        ),
        default=None,
    )
    sex: str | None = pydantic.Field(
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

    def _check_fields(self, file_paths: list[pathlib.Path]) -> None:
        # Check if values are specified
        if self.participant_id is None:
            self.messages.append(
                InspectionMessage(
                    title="Missing participant ID",
                    reason="BIDS requires a unique ID for all individual participants.",
                    solution="Specify the `subject_id` field of the Subject object attached to the NWB file.",
                    location_in_file="nwbfile.subject.subject_id",
                    file_paths=file_paths,
                    level=InspectionLevel.MISSING_BIDS_FIELD,
                )
            )
        if self.species is None:
            self.messages.append(
                InspectionMessage(
                    title="Missing participant species",
                    reason="Archives such as DANDI or EMBER require the subject species to be specified.",
                    solution=(
                        "Specify the `species` field of the Subject object attached to the NWB file as a "
                        "Latin binomial, obolibrary taxonomy link, or NCBI taxonomy reference."
                    ),
                    location_in_file="nwbfile.subject.species",
                    file_paths=file_paths,
                    level=InspectionLevel.MISSING_ARCHIVE_FIELD,
                )
            )
        if self.sex is None:
            self.messages.append(
                InspectionMessage(
                    title="Missing participant sex",
                    reason="Archives such as DANDI or EMBER require the subject sex to be specified.",
                    solution=(
                        "Specify the `sex` field of the Subject object attached to the NWB file as one of four "
                        'options: "M" (for male), "F" (for female), "U" (for unknown), or "O" (for other).\n'
                        "NOTE: for certain animal species with more specific genetic determinants, such as C elegans, "
                        'use "O" (for other) then further specify the subtypes using other custom fields. For example, '
                        '`c_elegans_sex="XO"`'
                    ),
                    location_in_file="nwbfile.subject.sex",
                    file_paths=file_paths,
                    level=InspectionLevel.MISSING_ARCHIVE_FIELD,
                )
            )

        # Check if specified values are valid
        if (
            self.participant_id is not None
            and re.match(pattern=_VALID_PARTICIPANT_ID_REGEX, string=self.participant_id) is None
        ):
            self.messages.append(
                InspectionMessage(
                    title="Invalid participant ID",
                    reason=(
                        "The participant ID contains invalid characters. "
                        "BIDS allows only dashes to be used as separators in subject entity label. "
                        "Underscores, spaces, slashes, and special characters (including #) are expressly forbidden."
                    ),
                    solution="Rename the participants without using spaces or underscores.",
                    examples=[
                        "`ab_01` -> `ab-01`",
                        "`subject #2` -> `subject-2`",
                        "`id 2 from 9/1/25` -> `id-2-9-1-25`",
                    ],
                    location_in_file="nwbfile.subject.subject_id",
                    file_paths=file_paths,
                    level=InspectionLevel.INVALID_BIDS_VALUE,
                )
            )
        if self.species is not None and re.match(pattern=_VALID_SPECIES_REGEX, string=self.species) is None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid species",
                    reason="Subject species is not a proper Latin binomial or NCBI Taxonomy id.",
                    solution=(
                        "Rename the participants species to a Latin binomial, obolibrary taxonomy link, or "
                        "NCBI taxonomy reference."
                    ),
                    examples=[],
                    location_in_file="nwbfile.subject.species",
                    file_paths=file_paths,
                    level=InspectionLevel.INVALID_ARCHIVE_VALUE,
                )
            )
        if self.sex is not None and _VALID_BIDS_SEXES.get(self.sex, None) is None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid subject sex (BIDS)",
                    reason="Subject sex is not one of the allowed patterns by BIDS.",
                    solution="Rename the subject sex to be one of the accepted values.",
                    examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
                    location_in_file="nwbfile.subject.sex",
                    file_paths=file_paths,
                    level=InspectionLevel.INVALID_BIDS_VALUE,
                )
            )

        if self.sex is not None and _VALID_ARCHIVES_SEXES.get(self.sex, None) is None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid subject sex (archives)",
                    reason="Subject sex is not one of the allowed patterns by the common archives.",
                    solution="Rename the subject sex to be one of the accepted values.",
                    examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
                    location_in_file="nwbfile.subject.sex",
                    file_paths=file_paths,
                    level=InspectionLevel.INVALID_ARCHIVE_VALUE,
                )
            )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self:
        """
        Extracts participant metadata from the in-memory NWBFile objects.
        """
        file_paths = [nwbfile.container_source for nwbfile in nwbfiles]

        messages = []
        if len(nwbfiles) > 1:
            messages.append(
                InspectionMessage(
                    title="NotImplemented: multiple NWB files",
                    reason=(
                        "The `Participant` model for `nwb2bids` does not yet support multiple NWB files. "
                        "Only the first will be used."
                    ),
                    solution="`nwb2bids` plans to add support for multiple NWB files in the future.",
                    file_paths=file_paths,
                    level=InspectionLevel.NOT_IMPLEMENTED,
                )
            )

        nwbfile = nwbfiles[0]

        if nwbfile.subject is None:
            messages.append(
                InspectionMessage(
                    title="Missing subject",
                    reason="BIDS requires a subject to be specified for each NWB file.",
                    solution="Add a Subject object to each NWB file.",
                    location_in_file="nwbfile.subject",
                    file_paths=file_paths,
                    level=InspectionLevel.MISSING_BIDS_ENTITY,
                )
            )
            participant = cls(messages=messages)
            return participant

        participant = cls(
            participant_id=nwbfile.subject.subject_id,
            species=nwbfile.subject.species,
            sex=nwbfile.subject.sex,
            strain=nwbfile.subject.strain,
            messages=messages,
            # TODO: add more
            # birthday=nwbfile.participant.date_of_birth,
            # age=nwbfile.participant.age
        )
        participant._check_fields(file_paths=file_paths)
        return participant
