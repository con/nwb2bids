# CHANGELOG

# Upcoming


# v0.3.0

# Deprecations

The CLI call `nwb2bids reposit` and API function `nwb2bids.reposit` have been removed - please use `nwb2bids convert` and `nwb2bids.convert_nwb_dataset` instead.

The API instantiation method `.from_nwb_directory` has been standardized as `.from_nwb_paths` and now takes an iterable of either file or directory paths.

# Features

The CLI now accepts a list of space-separated NWB file paths as input, enabling more robust wildcard syntax or `xargs` usage.
For example:
 - `nwb2bids convert file1.nwb file2.nwb`
 - `nwb2bids convert file*.nwb`
 - `find -iname "file*.nwb" | xargs nwb2bids convert`

Added an API argument `nwb_paths: list[str | pathlib.Path]` to all relevant conversion functions.

# Improvements

The BIDS directory arguments to the CLI (`--bids-directory`/`-o`) and API (`bids_directory`) are now optional, with the default case being the current working directory (which must be either empty or BIDS-compatible).

The default of all `file_mode` arguments is now the string `"auto"` instead of `None`.

# Fixes

Ensured removal of any temporary directory created by `BaseConverter._handle_file_mode()`. @candleindark [PR #44](https://github.com/con/nwb2bids/pull/44)

# Documentation

Updated README to accurately reflect CLI call syntax.



# v0.2.0

# Deprecations

The function `nwb2bids.reposit` has been soft deprecated - please use `nwb2bids.convert_nwb_dataset` instead.

# Features

Added events table support.

Added ability to specify additional metadata to write into the BIDS dataset.

Added new object-oriented API, complete with Pydantic model validation, has been added in the form of `nwb2bids.DatasetConverter`, `nwb2bids.SessionConverter`, and the `nwb2bids.bids_models` submodule.

# Improvements

Refactored source code to modern Python packaging standards.

# Fixes

Debugged ecephys structure against BEP032 BIDS schema current to 6/26/2025.



# v0.0.3

fixed sanitization syntax, added more robust tests



# v0.0.2

Make tests ignore order of files



# v0.0.1

Update proper file names
