import functools
import pathlib

from ._common import _sanitize_label
from ._levels import SanitizationLevel


@functools.cache
def sanitize_session_id(
    session_id: str,
    sanitization_level: SanitizationLevel = SanitizationLevel.NONE,
    sanitization_file_path: pathlib.Path | None = None,
    sanitization_report_context: str | None = None,
) -> str:
    """
    Sanitize a session ID.

    Parameters
    ----------
    session_id : str
        The original session ID to be sanitized.

    Returns
    -------
    sanitized_session_id : str
        The sanitized session ID label (without the 'ses-' entity prefix).
    sanitization_file_path : file path, optional
        The path to a file where a report of the sanitization actions taken will be written.
        If None, no report is written.
    sanitization_report_context : str, optional
        Additional context to include in the sanitization report (e.g., the name or scope of the calling method).
    """
    if sanitization_level > SanitizationLevel.NONE:
        sanitized_session_id = _sanitize_label(label=session_id)

        if sanitization_file_path is not None:
            sanitization_text = f"{sanitization_report_context}\n\t" if sanitization_report_context is not None else ""
            sanitization_text += f"Session ID: '{session_id}' -> '{sanitized_session_id}'.\n"
            with sanitization_file_path.open(mode="a") as report_file:
                report_file.write(sanitization_text)

        return sanitized_session_id
    return session_id
