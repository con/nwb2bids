<p align="center">
  <h1 align="center">nwb2bids</h3>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/nwb2bids.svg"></a>
    <a href="https://codecov.io/github/con/nwb2bids?branch=main"><img alt="codecov" src="https://codecov.io/github/con/nwb2bids/coverage.svg?branch=main"></a>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="PyPI latest release version" src="https://badge.fury.io/py/nwb2bids.svg?id=py&kill_cache=1"></a>
    <a href="https://github.com/con/nwb2bids/blob/main/LICENSE.txt"><img alt="License: BSD-3" src="https://img.shields.io/pypi/l/nwb2bids.svg"></a>
  </p>
  <p align="center">
    <a href="https://github.com/psf/black"><img alt="Python code style: Black" src="https://img.shields.io/badge/python_code_style-black-000000.svg"></a>
    <a href="https://github.com/astral-sh/ruff"><img alt="Python code style: Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  </p>
</p>

# nwb2bids

Reorganize NWB files into a BIDS directory layout.

Currently developed for the `microephys` BIDS modality, which encompasses both the NWB `ecephys` and `icephys` neurodata subtypes, and which is currently pending formal inclusion in BIDS schema as part of [BEP032](https://github.com/bids-standard/bids-specification/pull/1705).

# Usage

The package ships the `nwb2bids` CLI command.

```bash
nwb2bids < directory of NWB files > < BIDS organized directory >
```

For example:

```bash
nwb2bids /mnt/my_existing_nwbfiles/ /mnt/my_new_bids_dataset/
```
