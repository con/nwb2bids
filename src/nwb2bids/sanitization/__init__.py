"""
Collection of sanitization procedures to apply per field.

'Sanitization' in this sense means taking the NWB values for various fields, such as labels, and transforming them
to conform to BIDS.

Enabling more types of sanitization increases the validity of the resulting BIDS dataset.
"""

from ._configuration import SanitizationConfig
from ._sanitization import Sanitization

__all__ = [
    "Sanitization",
    "SanitizationConfig",
]
