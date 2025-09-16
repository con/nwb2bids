import functools
import pathlib

import pynwb


@functools.cache
def cache_read_nwb(file_path: pathlib.Path) -> pynwb.NWBFile:
    """Cache the read operation per NWB file path to speed up repeated calls."""
    nwbfile = pynwb.read_nwb(path=file_path)
    return nwbfile
