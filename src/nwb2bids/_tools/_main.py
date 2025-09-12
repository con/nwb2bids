import functools

import pynwb

read_nwb_memoize = functools.lru_cache(pynwb.read_nwb)
"""
A memoizing callable that wraps `pynwb.read_nwb`

It passes all arguments to `pynwb.read_nwb`, caches and returns the result.
"""
