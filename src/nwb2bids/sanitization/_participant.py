import functools
import re

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
        participant_id = re.sub(pattern=r"[^a-zA-Z0-9]", repl="+", string=participant_id)
    return participant_id
