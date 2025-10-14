<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/con/nwb2bids/main/assets/nwb2bids-color-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/con/nwb2bids/main/assets/nwb2bids-color.svg">
    <img alt="nwb2bids logo" src="https://raw.githubusercontent.com/con/nwb2bids/main/assets/nwb2bids-color.svg" width="200">
  </picture>

  <h1 align="center">nwb2bids</h1>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/nwb2bids.svg"></a>
    <a href="https://codecov.io/github/con/nwb2bids?branch=main"><img alt="codecov" src="https://codecov.io/github/con/nwb2bids/coverage.svg?branch=main"></a>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="PyPI latest release version" src="https://badge.fury.io/py/nwb2bids.svg?id=py&kill_cache=1"></a>
    <a href="https://github.com/con/nwb2bids/blob/main/LICENSE.txt"><img alt="License: BSD-3" src="https://img.shields.io/pypi/l/nwb2bids.svg"></a>
    <a href="https://doi.org/10.5281/zenodo.17148059"><img src="https://zenodo.org/badge/765478037.svg" alt="DOI"></a>
  </p>
  <p align="center">
    <a href="https://github.com/psf/black"><img alt="Python code style: Black" src="https://img.shields.io/badge/python_code_style-black-000000.svg"></a>
    <a href="https://github.com/astral-sh/ruff"><img alt="Python code style: Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  </p>
</p>

Reorganize NWB files into a BIDS directory layout.

Currently developed for the `microephys` BIDS modality, which encompasses both the NWB `ecephys` and `icephys` neurodata subtypes, and which is currently pending formal inclusion in BIDS schema as part of [BEP032](https://github.com/bids-standard/bids-specification/pull/1705).

# Usage

The package ships the `nwb2bids` CLI command.

```bash
nwb2bids convert <directory of NWB files> <BIDS organized directory>
```

For example:

```bash
nwb2bids convert /mnt/my_existing_nwbfiles/ /mnt/my_new_bids_dataset/
```

## Releasing

This repo uses Auto (https://github.com/intuit/auto) with hatch-vcs to cut releases from PR labels. Maintainership flow:

- One-time setup: run the GitHub Action "Setup Release Labels" to create Auto's full default label set in this repo (includes the semver labels and other labels used by Auto and enabled plugins).
- For a release PR: add both of the following labels to the PR before merging:
  - One semver label: `major`, `minor`, or `patch` (controls version bump)
  - The `release` label (authorizes publishing)
- After merge to `main`, the "Release with Auto" workflow will:
  - Compute the next version from labels on merged PRs
  - Create and push a Git tag (e.g., `v1.2.3`) and a GitHub Release with a changelog
- When the GitHub Release is published, the existing "Upload Package to PyPI" workflow builds from that tag and uploads to PyPI. The version is derived from the Git tag via `hatch-vcs`.

Notes:
- Only PRs with the `release` label will trigger a release; other PRs are collected until a release-labeled PR is merged.
- You can trigger a release manually via the "Release with Auto" workflow dispatch if needed.
- If labels ever get out of sync, re-run the "Setup Release Labels" workflow to re-seed the full set.
