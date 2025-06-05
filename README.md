# nwb2bids

This package helps reorganize your NWB data into a BIDS directory layout.

Currently developed for the `ephys` datatype, which is pending formal inclusion in BIDS as part of [BEP032](https://github.com/bids-standard/bids-specification/pull/1705).

# Usage

The package ships the `nwb2bids` CLI command.

```bash
nwb2bids reposit /nwb/file/directory /where/you/want/bids/to/be/written
```
