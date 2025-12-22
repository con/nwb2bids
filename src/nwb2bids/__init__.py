"""
NWB2BIDS
========

Reorganize NWB files into a BIDS directory layout.
"""

from ._core._convert_nwb_dataset import convert_nwb_dataset
from ._converters._dataset_converter import DatasetConverter
from ._converters._session_converter import SessionConverter
from ._converters._run_config import RunConfig
from ._inspection._inspection_result import InspectionResult, Severity, Category, DataStandard

__all__ = [
    # Public methods and classes
    "convert_nwb_dataset",
    "RunConfig",
    "DatasetConverter",
    "SessionConverter",
    "DataStandard",
    "InspectionResult",
    "Category",
    "Severity",
    # Public submodules
    "bids_models",
    "sanitization",
    "testing",
]

# Trigger import of hidden submodule elements (only need to import one item to trigger the rest)
from ._hidden_top_level_imports import _hide
