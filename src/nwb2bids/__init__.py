"""
NWB2BIDS
========

Reorganize NWB files into a BIDS directory layout.
"""

from __future__ import annotations

from ._base import convert_nwb_dataset
from ._base import DatasetConverter, SessionConverter

__all__ = [
    # Public methods and classes
    "convert_nwb_dataset",
    "DatasetConverter",
    "SessionConverter",
    # Public submodules
    "bids_models",
    "testing",
]

# Trigger import of hidden submodule elements (only need to import one item to trigger the rest)
from ._hidden_top_level_imports import _hide
