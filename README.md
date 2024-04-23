# nwb2bids

This package helps reorganize your NWB data into a BIDS directory layout.

It's currently developed for the `ephys` datatype, which is pending formal inclusion in BIDS as part of BEP032. 

# Usage

The package ships the `nwb2bids` CLI command.

```bash
nwb2bids reposit /nwb/file/directory /where/you/want/bids/to/be/written
```
