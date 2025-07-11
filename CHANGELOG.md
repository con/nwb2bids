# CHANGELOG

# Upcoming



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
