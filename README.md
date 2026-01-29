<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/con/nwb2bids/main/docs/assets/nwb2bids-color-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/con/nwb2bids/main/docs/assets/nwb2bids-color.svg">
    <img alt="nwb2bids logo" src="https://raw.githubusercontent.com/con/nwb2bids/main/docs/assets/nwb2bids-color.svg" width="200">
  </picture>

  <h1 align="center">nwb2bids</h1>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/nwb2bids.svg"></a>
    <a href="https://codecov.io/github/con/nwb2bids?branch=main"><img alt="codecov" src="https://codecov.io/github/con/nwb2bids/coverage.svg?branch=main"></a>
    <a href="https://nwb2bids.readthedocs.io/"><img alt="Documentation Status" src="https://readthedocs.org/projects/nwb2bids/badge/?version=latest"></a>
    <a href="https://github.com/con/nwb2bids/actions/workflows/daily_tests.yml/badge.svg"><img alt="Daily tests" src="https://github.com/con/nwb2bids/actions/workflows/daily_tests.yml/badge.svg"></a>
    <a href="https://github.com/con/nwb2bids/actions/workflows/daily_remote_tests.yml/badge.svg"><img alt="Daily tests (remote)" src="https://github.com/con/nwb2bids/actions/workflows/daily_remote_tests.yml/badge.svg"></a>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/nwb2bids/"><img alt="PyPI latest release version" src="https://badge.fury.io/py/nwb2bids.svg?id=py&kill_cache=1"></a>
    <a href="https://github.com/con/nwb2bids/blob/main/LICENSE.txt"><img alt="License: BSD-3" src="https://img.shields.io/pypi/l/nwb2bids.svg"></a>
    <a href="https://zenodo.org/badge/latestdoi/765478037"><img alt="DOI" src="https://img.shields.io/github/v/release/con/nwb2bids?label=DOI&color=blue"></a>
  </p>
  <p align="center">
    <a href="https://github.com/psf/black"><img alt="Python code style: Black" src="https://img.shields.io/badge/python_code_style-black-000000.svg"></a>
    <a href="https://github.com/astral-sh/ruff"><img alt="Python code style: Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  </p>
</div>

**nwb2bids** reorganizes [NWB](https://www.nwb.org/) (Neurodata Without Borders) files into a [BIDS](https://bids.neuroimaging.io/) (Brain Imaging Data Structure) directory layout, making your neurophysiology data more accessible and shareable.

## Features

- **Automatic conversion**: Renames NWB files and directories to conform to BIDS conventions
- **Metadata extraction**: Populates BIDS sidecar TSV & JSON files from NWB metadata
- **BEP032 support**: Currently supports micro-electrode electrophysiology (extracellular `ecephys` and intracellular `icephys`) and associated behavioral events per [BEP032](https://github.com/bids-standard/bids-specification/pull/1705)
- **Remote datasets**: Works with datasets hosted on [DANDI Archive](https://dandiarchive.org/)

## Installation

Install the latest stable release using pip or conda:

```bash
# Using pip
pip install nwb2bids

# Using conda
conda install -c conda-forge nwb2bids
```

To work with datasets on DANDI Archive, install with the `dandi` extra:

```bash
pip install "nwb2bids[dandi]"
```

## Quick Start

### Command Line Interface

Convert NWB files to BIDS from the command line:

```bash
# Convert files from a directory
nwb2bids convert path/to/nwb/files/

# Specify output directory
nwb2bids convert path/to/nwb/files/ --bids-directory path/to/bids/output/

# Convert multiple sources
nwb2bids convert path/to/directory/ single_file.nwb another_file.nwb
```

### Python API

Use nwb2bids programmatically:

```python
import nwb2bids

# Convert NWB files to BIDS
nwb2bids.convert_nwb_dataset(
    nwb_paths=["path/to/nwb/files/"],
    run_config=nwb2bids.RunConfig(bids_directory="path/to/bids/output/")
)
```

## Use Cases

**nwb2bids** was developed to support the [DANDI Archive](https://dandiarchive.org/) project, enabling researchers to convert neurophysiology datasets from NWB to BIDS format.

### Working with BIDS Dandisets

The [bids-dandisets organization](https://github.com/bids-dandisets/) hosts BIDS-formatted versions of datasets from DANDI Archive. You can:

- Browse converted datasets at [github.com/bids-dandisets](https://github.com/bids-dandisets/)
- Track conversion progress via the [dashboard](https://github.com/bids-dandisets/dashboard?tab=readme-ov-file)
- Access datasets efficiently using [DataLad](https://www.datalad.org/) for version-controlled data management

## Documentation

For comprehensive information, please visit our full documentation:

📖 **[nwb2bids.readthedocs.io](https://nwb2bids.readthedocs.io/)**

The documentation includes:
- [User Guide](https://nwb2bids.readthedocs.io/en/latest/user_guide.html) - Detailed usage instructions and advanced features
- [Tutorials](https://nwb2bids.readthedocs.io/en/latest/tutorials.html) - Step-by-step examples
- [API Reference](https://nwb2bids.readthedocs.io/en/latest/api/index.html) - Complete function and class documentation
- [Developer Guide](https://nwb2bids.readthedocs.io/en/latest/developer_guide.html) - Contributing guidelines

## Contributing

We welcome contributions! Please see our [Developer Guide](https://nwb2bids.readthedocs.io/en/latest/developer_guide.html) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
