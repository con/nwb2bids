# v0.5.1 (Thu Oct 23 2025)

#### 🐛 Bug Fix

- Trivial change for release test [#152](https://github.com/con/nwb2bids/pull/152) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Resolve protected branch problem in execution of the "Release with Auto" GH workflow [#151](https://github.com/con/nwb2bids/pull/151) ([@candleindark](https://github.com/candleindark))
- bf: always include session entity, even 1 sub [#148](https://github.com/con/nwb2bids/pull/148) ([@asmacdo](https://github.com/asmacdo))
- [pre-commit.ci] pre-commit autoupdate [#146](https://github.com/con/nwb2bids/pull/146) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Add macos-15-intel runner; deprecate macos-13; remove temporary pin on h5py [#145](https://github.com/con/nwb2bids/pull/145) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Document how to install and run tests locally [#144](https://github.com/con/nwb2bids/pull/144) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Move repo files under .github [#143](https://github.com/con/nwb2bids/pull/143) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- add contributing file [#142](https://github.com/con/nwb2bids/pull/142) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Fill in docs [#139](https://github.com/con/nwb2bids/pull/139) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Improve and consolidate release and deploy workflow [#138](https://github.com/con/nwb2bids/pull/138) ([@candleindark](https://github.com/candleindark))
- Provide fix for Setup Release Labels workflow [#137](https://github.com/con/nwb2bids/pull/137) ([@candleindark](https://github.com/candleindark))
- Automate release and versioning with AUTO and `hatch-vcs` [#114](https://github.com/con/nwb2bids/pull/114) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#134](https://github.com/con/nwb2bids/pull/134) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Update email notification conditions and body URL [#135](https://github.com/con/nwb2bids/pull/135) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Blacklist h5py version dependency for macOS platform [#136](https://github.com/con/nwb2bids/pull/136) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Fixup rtd build [#131](https://github.com/con/nwb2bids/pull/131) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- add logo for dark theme [#127](https://github.com/con/nwb2bids/pull/127) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Remove project title from README [#125](https://github.com/con/nwb2bids/pull/125) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Add daily tests and notifications [#110](https://github.com/con/nwb2bids/pull/110) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Add ability to read from raw dandiset metadata when invalid [#107](https://github.com/con/nwb2bids/pull/107) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Set the default python version in a Hatch-managed environment to the project's lowest support Python version [#117](https://github.com/con/nwb2bids/pull/117) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Upgrade to rich-click [#121](https://github.com/con/nwb2bids/pull/121) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#122](https://github.com/con/nwb2bids/pull/122) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Update logo image source in README.md [#120](https://github.com/con/nwb2bids/pull/120) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### ⚠️ Pushed to `main`

- fix: hotfix failure point ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### Authors: 4

- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Austin Macdonald ([@asmacdo](https://github.com/asmacdo))
- Cody Baker ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Isaac To ([@candleindark](https://github.com/candleindark))

---

# CHANGELOG

# Upcoming


# v0.5.1

# Fixes

Fixed a bug where failure points would not be captured and reported as notifications.



# v0.5.0

# Features

Added a notification system via the return of `nwb2bids.convert_nwb_dataset` and attached as the `.messages` attribute to all converter objects.

# Improvements

Began filtering benign PyNWB warnings during read operations.

# Documentation

Preliminary documentation is now available at [nwb2bids.readthedocs.io](https://nwb2bids.readthedocs.io/en/latest/).



# v0.4.0

# Features

Added a `.from_remote_dandiset` instantiation method for the `DatasetConverter` class. This requires installing the `pip install nwb2bids[dandi]` extra dependencies.



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
