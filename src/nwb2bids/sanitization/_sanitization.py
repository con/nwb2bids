import pathlib
import typing

import pydantic

from ._common import _sanitize_label
from ._levels import SanitizationLevel


class Sanitization(pydantic.BaseModel):
    """
    Sanitize all relevant metadata fields when translating from minimal NWB towards valid BIDS.

    sanitization_level : SanitizationLevel
        The level of sanitization to apply.
        See `nwb2bids.sanitization.SanitizationLevel?` for more details.
    sanitization_file_path : pathlib.Path
        The file to save a record of sanitization actions taken.
    original_session_id : str
        The original session ID to be sanitized.
    original_participant_id : str
        The original participant ID to be sanitized.
    sanitized_session_id : str
        The sanitized session ID label.
    sanitized_participant_id : str
        The sanitized participant ID label.
    """

    sanitization_level: SanitizationLevel
    sanitization_file_path: pathlib.Path
    original_session_id: str
    original_participant_id: str
    sanitized_session_id: str | None = None
    sanitized_participant_id: str | None = None

    def model_post_init(self, context: typing.Any, /) -> None:
        """Save the sanitization actions to the report file (unless level is 0)."""
        fields_to_sanitize = [self.sanitized_session_id, self.sanitized_participant_id]
        if any(field_to_sanitize is not None for field_to_sanitize in fields_to_sanitize):
            message = "Sanitized IDs should not be provided during initialization."
            raise ValueError(message)

        self.sanitized_session_id = _sanitize_label(
            label=self.original_session_id, sanitization_level=self.sanitization_level
        )
        self.sanitized_participant_id = _sanitize_label(
            label=self.original_participant_id, sanitization_level=self.sanitization_level
        )

        sanitization_lines = [
            f"Session ID: '{self.original_session_id}' -> '{self.sanitized_session_id}'",
            f"Participant ID: '{self.original_participant_id}' -> '{self.sanitized_participant_id}'",
        ]
        sanitization_text = "\n".join(sanitization_lines)
        with self.sanitization_file_path.open(mode="a") as file_stream:
            file_stream.write(sanitization_text)
