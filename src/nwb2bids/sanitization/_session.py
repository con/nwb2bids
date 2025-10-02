import functools

from ._common import _sanitize_label
from ._levels import SanitizationLevel


@functools.lru_cache(maxsize=None)
def sanitize_session_id(session_id: str, sanitization_level: SanitizationLevel = SanitizationLevel.NONE) -> str:
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
    """
    if sanitization_level > SanitizationLevel.NONE:
        sanitized_session_id = _sanitize_label(label=session_id)
    return sanitized_session_id
