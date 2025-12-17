import pathlib
import re
import typing

import pydantic

from ._configuration import SanitizationConfig


class Sanitization(pydantic.BaseModel):
    """
    Sanitize all relevant metadata fields when translating from minimal NWB towards valid BIDS.

    sanitization_config : SanitizationConfig
        The types of sanitization to apply.
        See `nwb2bids.sanitization.SanitizationConfig?` for more details.
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

    sanitization_config: SanitizationConfig
    sanitization_file_path: pathlib.Path
    original_participant_id: str
    original_session_id: str

    def model_post_init(self, context: typing.Any, /) -> None:
        with self.sanitization_file_path.open(mode="w") as file_stream:
            file_stream.write(self.model_dump_json())

    @staticmethod
    def _sanitize_label(label: str) -> str:
        """Sanitize a generic entity label by replacing non-alphanumeric characters with plus signs."""
        sanitized_label = re.sub(pattern=r"[^a-zA-Z0-9]", repl="+", string=label).removeprefix("+").removesuffix("+")
        return sanitized_label

    @pydantic.computed_field
    @property
    def sanitized_participant_id(self) -> str | None:
        if self.sanitization_config.sub_labels is False:
            return self.original_participant_id
        return self._sanitize_label(label=self.original_participant_id)

    @pydantic.computed_field
    @property
    def sanitized_session_id(self) -> str | None:
        if self.sanitization_config.ses_labels is False:
            return self.original_session_id
        return self._sanitize_label(label=self.original_session_id)
