"""
Collection of sanitization procedures to apply per field.

'Sanitization' in this sense means taking the NWB values for various fields, such as labels, and transforming them
to conform to BIDS.

Increasing the level of sanitization increases the validity of the resulting BIDS dataset.
"""

from ._levels import SanitizationLevel
from ._participant import sanitize_participant_id
from ._session import sanitize_session_id

__all__ = [
    "SanitizationLevel",
    "sanitize_participant_id",
    "sanitize_session_id",
]
