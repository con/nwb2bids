import functools
import pathlib

from ._common import _sanitize_label
from ._levels import SanitizationLevel


@functools.cache
def sanitize_participant_id(
    participant_id: str,
    sanitization_level: SanitizationLevel = SanitizationLevel.NONE,
    sanitization_file_path: pathlib.Path | None = None,
    sanitization_report_context: str | None = None,
) -> str:
    """
    Sanitize a participant ID.

    Parameters
    ----------
    participant_id : str
        The original subject ID to be sanitized.
    sanitization_level : SanitizationLevel, optional
        The level of sanitization to apply. Default is `SanitizationLevel.NONE`.
    sanitization_file_path : file path, optional
        The path to a file where a report of the sanitization actions taken will be written.
        If None, no report is written.
    sanitization_report_context : str, optional
        Additional context to include in the sanitization report (e.g., the name or scope of the calling method).

    Returns
    -------
    sanitized_participant_id : str
        The sanitized participant ID label (without the 'sub-' entity prefix).
    """
    if sanitization_level > SanitizationLevel.NONE:
        sanitized_participant_id = _sanitize_label(label=participant_id)

        if sanitization_file_path is not None:
            sanitization_text = f"{sanitization_report_context}\n\t" if sanitization_report_context is not None else ""
            sanitization_text += f"Participant ID: '{participant_id}' -> '{sanitized_participant_id}'.\n"
            with sanitization_file_path.open(mode="a") as report_file:
                report_file.write(sanitization_text)

        return sanitized_participant_id
    return participant_id
