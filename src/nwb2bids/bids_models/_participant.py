import re
from typing import Any

import pydantic
import pynwb
import typing_extensions

from ._model_globals import _ALLOWED_SEXES, _INVALID_PARTICIPANT_ID_REGEX, _VALID_SPECIES_REGEX
from .._messages._inspection_message import InspectionMessage
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

    def model_post_init(self, context: Any, /) -> None:
        if re.match(pattern=_INVALID_PARTICIPANT_ID_REGEX, string=self.participant_id) is not None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid participant ID",
                    text=(
                        "The participant ID contains underscores; these will be forcibly converted to dashes in the "
                        "filename and table references. For consistency, please rename the participants using no "
                        "spaces or underscores."
                    ),
                    level=2,
                )
            )

        if self.species is not None and re.match(pattern=_VALID_SPECIES_REGEX, string=self.species) is None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid species",
                    text="Subject species is not a proper Latin binomial or NCBI Taxonomy id.",
                    level=2,
                )
            )

        if self.sex is not None and _ALLOWED_SEXES.get(self.sex, None) is None:
            self.messages.append(
                InspectionMessage(
                    title="Invalid sex",
                    text="Subject sex is not one of the allowed patterns.",
                    level=2,
                )
            )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self:
        """
        Extracts participant metadata from the in-memory NWBFile objects.
        """
        messages = []
        if len(nwbfiles) > 1:
            messages.append(
                InspectionMessage(
                    title="NotImplemented: multiple NWB files",
                    text=(
                        "The `Participant` model for `nwb2bids` does not yet support multiple NWB files. "
                        "Only the first will be used."
                    ),
                    level=0,
                )
            )

        nwbfile = nwbfiles[0]

        subject = cls(
            participant_id=nwbfile.subject.subject_id,
            species=nwbfile.subject.species,
            sex=nwbfile.subject.sex,
            strain=nwbfile.subject.strain,
            messages=messages,
            # TODO: add more
            # birthday=nwbfile.participant.date_of_birth,
            # age=nwbfile.participant.age
        )
        return subject
