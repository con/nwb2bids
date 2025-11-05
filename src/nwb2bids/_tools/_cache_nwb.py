import functools
import pathlib
import warnings

import pynwb

ignored_pynwb_message_patterns = [
    "No cached namespaces found in .+",
    "Ignoring cached namespace .+",
    "Ignoring the following cached .+",
    "Stimulus description 'NA' for .+",
    "Use of icephys_filtering is deprecated and will be removed .+",
    "Date is missing timezone .+",
]
for message in ignored_pynwb_message_patterns:
    warnings.filterwarnings(action="ignore", message=message)


@functools.cache
def cache_read_nwb(file_path: pathlib.Path) -> pynwb.NWBFile:
    """Cache the read operation per NWB file path to speed up repeated calls."""
     # Always resolve in case of symlinks, mostly relevant to Windows (i.e., from DataLad most likely)
    resolved_path = file_path.resolve()
    nwbfile = pynwb.read_nwb(path=resolved_path)
    return nwbfile
