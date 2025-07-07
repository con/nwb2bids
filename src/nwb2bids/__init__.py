"""
NWB2BIDS
========

Reorganize NWB files into a BIDS directory layout.
"""

from ._base import convert_nwb_dataset
from ._base import DatasetConverter, SessionConverter
from ._base._reposit import reposit

__all__ = [
    # Public methods and classes
    "convert_nwb_dataset",
    "reposit",  # TODO: remove
    "DatasetConverter",
    "SessionConverter",
    # Public submodules
    "bids_models",
    "testing",
]

# Trigger import of hidden submodule elements (only need to import one item to trigger the rest)
from ._hidden_top_level_imports import _hide
