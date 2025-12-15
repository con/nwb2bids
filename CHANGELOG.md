# v0.8.0 (Mon Dec 15 2025)

#### 🚀 Enhancement

- Added `HEDVersion` to dataset description [#232](https://github.com/con/nwb2bids/pull/232) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Replaced pytest/doctest with Sybil to add hidden assertions verifying tutorial outputs [#227](https://github.com/con/nwb2bids/pull/227) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Updated writing of channels TSV file [#225](https://github.com/con/nwb2bids/pull/225) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Updated writing of probes TSV file [#220](https://github.com/con/nwb2bids/pull/220) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🐛 Bug Fix

- Fixed confusing labels in `assert_subdirectory_structure` error messages [#228](https://github.com/con/nwb2bids/pull/228) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Updated writing of electrode TSV file [#221](https://github.com/con/nwb2bids/pull/221) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#223](https://github.com/con/nwb2bids/pull/223) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Fixed some test markers and imports based on latest conda-forge tests [#219](https://github.com/con/nwb2bids/pull/219) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### ⚠️ Pushed to `main`

- Fix typo in CHANGELOG.md ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🏠 Internal

- Restored intel runners [#233](https://github.com/con/nwb2bids/pull/233) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Config mypy [#229](https://github.com/con/nwb2bids/pull/229) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 📝 Documentation

- Updated DOI badge link in README [#230](https://github.com/con/nwb2bids/pull/230) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Added CITATION.cff to repository (to be used for all formal citations) [#224](https://github.com/con/nwb2bids/pull/224) ([@asmacdo](https://github.com/asmacdo))

#### Authors: 4

- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Austin Macdonald ([@asmacdo](https://github.com/asmacdo))
- Cody Baker ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Isaac To ([@candleindark](https://github.com/candleindark))

---

# v0.7.0 (Mon Dec 08 2025)

### Release Notes

#### Added and integrated a configuration model ([#164](https://github.com/con/nwb2bids/pull/164))

This release includes big changes to how arguments are passed in the `nwb2bids` API: the `RunConfig` object.

This class is a Pydantic model which encapsulates all previous configuration settings, such as the output BIDS directory and the additional metadata file path. This class is also now passed at time of initialization for all `Converter` classes and prior to calling the `convert_nwb_dataset` helper function. This reduces any confusion about which steps of the workflow take which arguments, and allows all internal actions to refer to the common location instead of having to manage passing values back-and-forth. It also has the added benefit of simplifying any future additions to configuration options, such as sanitization parameters.

CLI users are unaffected by these changes, aside from gaining a few new arguments - check them out with

```bash
nwb2bids convert --help
```

---

#### 🚀 Enhancement

- Enhance error notifications [#193](https://github.com/con/nwb2bids/pull/193) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) codycbakerphd@gmail.com)
- Added and integrated a configuration model [#164](https://github.com/con/nwb2bids/pull/164) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@candleindark](https://github.com/candleindark) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))

#### 🐛 Bug Fix

- Added automatic notification dump [#216](https://github.com/con/nwb2bids/pull/216) (codycbakerphd@gmail.com [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Aggregated unique values across participant rows [#206](https://github.com/con/nwb2bids/pull/206) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Skipped indexed columns; simplified skipping of timeseries [#205](https://github.com/con/nwb2bids/pull/205) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Added column metadata to sidecar files [#203](https://github.com/con/nwb2bids/pull/203) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Added tutorials to documentation [#173](https://github.com/con/nwb2bids/pull/173) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) codycbakerphd@gmail.com [@asmacdo](https://github.com/asmacdo))
- Fixed broken symlinking of source NWB file [#207](https://github.com/con/nwb2bids/pull/207) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Restrict sphinx version to below 9.0.0 [#201](https://github.com/con/nwb2bids/pull/201) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Fixed regression when `bids_directory` does not exist, automatically create it [#183](https://github.com/con/nwb2bids/pull/183) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#200](https://github.com/con/nwb2bids/pull/200) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Fix notification targets and add manual dispatch to daily tests [#196](https://github.com/con/nwb2bids/pull/196) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Corrected the labeling notification to proper BIDS [#176](https://github.com/con/nwb2bids/pull/176) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) codycbakerphd@gmail.com)
- Added GeneratedBy to `dataset_description.json` [#170](https://github.com/con/nwb2bids/pull/170) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#184](https://github.com/con/nwb2bids/pull/184) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Added support for operating on DataLad datasets [#165](https://github.com/con/nwb2bids/pull/165) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) codycbakerphd@gmail.com [@github-actions[bot]](https://github.com/github-actions[bot]))
- Revise config model [#175](https://github.com/con/nwb2bids/pull/175) ([@candleindark](https://github.com/candleindark))
- Automatic release [#157](https://github.com/con/nwb2bids/pull/157) ([@github-actions[bot]](https://github.com/github-actions[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Testing auto release (again) [#156](https://github.com/con/nwb2bids/pull/156) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🏠 Internal

- Completely remove macOS-13 from all workflows and split daily workflows into remote vs. non-remote [#194](https://github.com/con/nwb2bids/pull/194) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Reduced CodeCov spam [#161](https://github.com/con/nwb2bids/pull/161) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Automatic release [#155](https://github.com/con/nwb2bids/pull/155) ([@github-actions[bot]](https://github.com/github-actions[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 📝 Documentation

- Added container usage instructions [#209](https://github.com/con/nwb2bids/pull/209) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Improve README badge names [#195](https://github.com/con/nwb2bids/pull/195) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Add documentation link/badge to README [#186](https://github.com/con/nwb2bids/pull/186) ([@asmacdo](https://github.com/asmacdo))
- doc: clarify NWB_PATHS are space separated [#182](https://github.com/con/nwb2bids/pull/182) ([@asmacdo](https://github.com/asmacdo))
- Small CHANGELOG fixes [#166](https://github.com/con/nwb2bids/pull/166) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🧪 Tests

- Skip two DataLad tests in Windows CI [#197](https://github.com/con/nwb2bids/pull/197) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD) [@yarikoptic](https://github.com/yarikoptic))

#### 🔩 Dependency Updates

- [pre-commit.ci] pre-commit autoupdate [#204](https://github.com/con/nwb2bids/pull/204) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- [pre-commit.ci] pre-commit autoupdate [#192](https://github.com/con/nwb2bids/pull/192) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#174](https://github.com/con/nwb2bids/pull/174) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- [pre-commit.ci] pre-commit autoupdate [#169](https://github.com/con/nwb2bids/pull/169) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))

#### Authors: 7

- [@github-actions[bot]](https://github.com/github-actions[bot])
- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Austin Macdonald ([@asmacdo](https://github.com/asmacdo))
- Cody Baker ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- CodyCBakerPhD (codycbakerphd@gmail.com)
- Isaac To ([@candleindark](https://github.com/candleindark))
- Yaroslav Halchenko ([@yarikoptic](https://github.com/yarikoptic))

---

# v0.6.0 (Fri Oct 24 2025)

#### 🚀 Enhancement

- Always include session entity, even with only one subject [#148](https://github.com/con/nwb2bids/pull/148) ([@asmacdo](https://github.com/asmacdo))

#### 🐛 Bug Fix

- Testing auto release (again) [#156](https://github.com/con/nwb2bids/pull/156) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Testing auto release [#152](https://github.com/con/nwb2bids/pull/152) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Resolved protected branch problem in execution of the "Release with Auto" GH workflow [#151](https://github.com/con/nwb2bids/pull/151) ([@candleindark](https://github.com/candleindark))
- Add ability to read from raw dandiset metadata when invalid [#107](https://github.com/con/nwb2bids/pull/107) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Upgraded to `rich-click` backend for CLI [#121](https://github.com/con/nwb2bids/pull/121) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### ⚠️ Pushed to `main`

- fix: hotfix failure point ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🏠 Internal

- Automatic release [#155](https://github.com/con/nwb2bids/pull/155) ([@github-actions[bot]](https://github.com/github-actions[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Use two GitHub tokens in Release with Auto workflow [#154](https://github.com/con/nwb2bids/pull/154) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Improved and consolidated release and deploy workflow [#138](https://github.com/con/nwb2bids/pull/138) ([@candleindark](https://github.com/candleindark))
- Provided fix for Setup Release Labels workflow [#137](https://github.com/con/nwb2bids/pull/137) ([@candleindark](https://github.com/candleindark))
- Automated release and versioning with AUTO and `hatch-vcs` [#114](https://github.com/con/nwb2bids/pull/114) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Updated email notification conditions and body URL [#135](https://github.com/con/nwb2bids/pull/135) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Set the default python version in a Hatch-managed environment to the project's lowest support Python version [#117](https://github.com/con/nwb2bids/pull/117) ([@candleindark](https://github.com/candleindark) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 📝 Documentation

- Document how to install and run tests locally [#144](https://github.com/con/nwb2bids/pull/144) ([@asmacdo](https://github.com/asmacdo) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Moved repo files under `.github` [#143](https://github.com/con/nwb2bids/pull/143) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Added contributing file [#142](https://github.com/con/nwb2bids/pull/142) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Filled in docs [#139](https://github.com/con/nwb2bids/pull/139) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Fixed RTD build [#131](https://github.com/con/nwb2bids/pull/131) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Added logo for dark theme [#127](https://github.com/con/nwb2bids/pull/127) ([@asmacdo](https://github.com/asmacdo) [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Removed project title from README [#125](https://github.com/con/nwb2bids/pull/125) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Updated logo image source in `README.md` [#120](https://github.com/con/nwb2bids/pull/120) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🧪 Tests

- Add daily tests and notifications [#110](https://github.com/con/nwb2bids/pull/110) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))

#### 🔩 Dependency Updates

- [pre-commit.ci] pre-commit autoupdate [#146](https://github.com/con/nwb2bids/pull/146) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))
- Added `macos-15-intel` runner; deprecate `macos-13`; removed temporary pin on `h5py` [#145](https://github.com/con/nwb2bids/pull/145) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#134](https://github.com/con/nwb2bids/pull/134) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]) [@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Blacklisted `h5py` version dependency for macOS platform [#136](https://github.com/con/nwb2bids/pull/136) ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- [pre-commit.ci] pre-commit autoupdate [#122](https://github.com/con/nwb2bids/pull/122) ([@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot]))

#### Authors: 5

- [@github-actions[bot]](https://github.com/github-actions[bot])
- [@pre-commit-ci[bot]](https://github.com/pre-commit-ci[bot])
- Austin Macdonald ([@asmacdo](https://github.com/asmacdo))
- Cody Baker ([@CodyCBakerPhD](https://github.com/CodyCBakerPhD))
- Isaac To ([@candleindark](https://github.com/candleindark))


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
