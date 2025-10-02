import functools
import pathlib
import warnings

import pynwb

warnings.filterwarnings(action="ignore", message="No cached namespaces found in .+")
warnings.filterwarnings(action="ignore", message="Ignoring cached namespace .+")
warnings.filterwarnings(action="ignore", message="Stimulus description 'NA' for .+")
warnings.filterwarnings(action="ignore", message="Use of icephys_filtering is deprecated and will be removed .+")


@functools.cache
def cache_read_nwb(file_path: pathlib.Path) -> pynwb.NWBFile:
    """Cache the read operation per NWB file path to speed up repeated calls."""

    nwbfile = pynwb.read_nwb(path=file_path)
    return nwbfile
