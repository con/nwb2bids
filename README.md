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
    <a href="https://nwb2bids.readthedocs.io/"><img alt="Documentation Status" src="https://readthedocs.org/projects/nwb2bids/badge/?version=latest"></a>
    <a href="https://github.com/con/nwb2bids/actions/workflows/dailies.yml/badge.svg"><img alt="Daily tests" src="https://github.com/con/nwb2bids/actions/workflows/dailies.yml/badge.svg"></a>
    <a href="https://github.com/con/nwb2bids/actions/workflows/daily_remote.yml/badge.svg"><img alt="Daily tests (remote)" src="https://github.com/con/nwb2bids/actions/workflows/daily_remote.yml/badge.svg"></a>
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
