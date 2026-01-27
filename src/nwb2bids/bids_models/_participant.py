import pathlib
import re

import pydantic
import pynwb
import typing_extensions

from ._model_globals import _VALID_ARCHIVES_SEXES, _VALID_BIDS_SEXES, _VALID_ID_REGEX, _VALID_SPECIES_REGEX
from ..bids_models._base_metadata_model import BaseMetadataModel
from ..notifications import Notification


class Participant(BaseMetadataModel):
    participant_id: str | None = pydantic.Field(
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

    def _check_fields(self, file_paths: list[pathlib.Path] | list[pydantic.HttpUrl]) -> None:
        # Check if values are specified
        if self.participant_id is None:
            notification = Notification.from_definition(identifier="MissingParticipantID", source_file_paths=file_paths)
            self.notifications.append(notification)
        if self.species is None:
            notification = Notification.from_definition(identifier="MissingSpecies", source_file_paths=file_paths)
            self.notifications.append(notification)
        if self.sex is None:
            notification = Notification.from_definition(
                identifier="MissingParticipantSex", source_file_paths=file_paths
            )
            self.notifications.append(notification)

        # Check if specified values are valid
        if (
            self.participant_id is not None
            and re.match(pattern=f"{_VALID_ID_REGEX}$", string=self.participant_id) is None
        ):
            notification = Notification.from_definition(identifier="InvalidParticipantID", source_file_paths=file_paths)
            self.notifications.append(notification)
        if self.species is not None and re.match(pattern=_VALID_SPECIES_REGEX, string=self.species) is None:
            notification = Notification.from_definition(identifier="InvalidSpecies", source_file_paths=file_paths)
            self.notifications.append(notification)
        if self.sex is not None and _VALID_BIDS_SEXES.get(self.sex, None) is None:
            notification = Notification.from_definition(
                identifier="InvalidParticipantSexBIDS", source_file_paths=file_paths
            )
            self.notifications.append(notification)

        if self.sex is not None and _VALID_ARCHIVES_SEXES.get(self.sex, None) is None:
            notification = Notification.from_definition(
                identifier="InvalidParticipantSexArchives", source_file_paths=file_paths
            )
            self.notifications.append(notification)

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self:
        """
        Extracts participant metadata from the in-memory NWBFile objects.
        """
        file_paths = [nwbfile.container_source for nwbfile in nwbfiles]

        notifications = []
        if len(nwbfiles) > 1:
            notification = Notification.from_definition(
                identifier="MultipleNWB:Participant", source_file_paths=file_paths
            )
            notifications.append(notification)

        nwbfile = nwbfiles[0]

        if nwbfile.subject is None:
            notification = Notification.from_definition(identifier="MissingParticipant", source_file_paths=file_paths)
            notifications.append(notification)
            participant = cls(
                notifications=notifications,
                participant_id="0",  # Similar to the missing session ID; let placeholder default to "0"
            )
            return participant

        participant = cls(
            participant_id=nwbfile.subject.subject_id,
            species=nwbfile.subject.species,
            sex=nwbfile.subject.sex,
            strain=nwbfile.subject.strain,
            notifications=notifications,
            # TODO: add more
            # birthday=nwbfile.participant.date_of_birth,
            # age=nwbfile.participant.age
        )
        participant._check_fields(file_paths=file_paths)
        return participant
