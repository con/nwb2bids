import functools

from ._common import _sanitize_label
from ._levels import SanitizationLevel


@functools.lru_cache(maxsize=None)
def sanitize_participant_id(participant_id: str, sanitization_level: SanitizationLevel = SanitizationLevel.NONE) -> str:
    """
    Sanitize a participant ID.

    Parameters
    ----------
    participant_id : str
        The original subject ID to be sanitized.

    Returns
    -------
    sanitized_participant_id : str
        The sanitized participant ID label (without the 'sub-' entity prefix).
    """
    if sanitization_level > SanitizationLevel.NONE:
        sanitized_participant_id = _sanitize_label(label=participant_id)
    return sanitized_participant_id
