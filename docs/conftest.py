"""Configuration file for sybil-based doc testing."""
import datetime
import json
import pathlib
import shutil
import subprocess
import uuid

import dateutil
import pandas
import pynwb
import pynwb.testing.mock.file
from sybil import Sybil
from sybil.parsers.rest import CodeBlockParser, PythonCodeBlockParser, SkipParser

import nwb2bids


def bash_evaluator(example):
    """Execute bash code blocks."""
    result = subprocess.run(
        example.parsed,
        shell=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Command failed (exit {result.returncode}):\n{result.stderr}"


def sybil_setup(namespace):
    """Clean and regenerate tutorial data before tests.

    NOTE: This runs once per document, not per code block. If multiple examples
    in the same document write to the same output directory, they will conflict.
    Use distinct output directories (e.g., bids_dataset_cli_1, bids_dataset_py_1).
    """
    tutorial_base = nwb2bids.testing.get_tutorial_directory()
    if tutorial_base.exists():
        shutil.rmtree(tutorial_base)

    nwb2bids.testing.generate_ephys_tutorial(mode="file")
    nwb2bids.testing.generate_ephys_tutorial(mode="dataset")

    # Create metadata.json for tutorials that need it
    tutorial_dir = tutorial_base / "ecephys_tutorial_file"
    (tutorial_dir / "metadata.json").write_text(json.dumps({
        "dataset_description": {
            "Name": "My Custom BIDS Dataset",
            "BIDSVersion": "1.8.0",
            "HEDVersion": "8.3.0",
            "Authors": ["First Last", "Second Author"]
        }
    }))

    # Run conversion for conversion_gallery.rst
    # This creates bids_dataset_py_1 for the conversion gallery examples
    nwb_path = tutorial_dir / "ecephys.nwb"
    bids_directory = tutorial_dir / "bids_dataset_py_1"
    bids_directory.mkdir(exist_ok=True)

    run_config = nwb2bids.RunConfig(bids_directory=bids_directory)
    nwb2bids.convert_nwb_dataset(
        nwb_paths=[nwb_path],
        run_config=run_config,
    )

    expected_files = pathlib.Path(__file__).parent / "expected_files"

    # Make common imports and paths available
    namespace["datetime"] = datetime
    namespace["dateutil"] = dateutil
    namespace["pathlib"] = pathlib
    namespace["uuid"] = uuid

    namespace["pandas"] = pandas
    namespace["pynwb"] = pynwb
    namespace["pynwb.ecephys"] = pynwb.ecephys
    namespace["nwb2bids"] = nwb2bids
    namespace["tutorial_base"] = tutorial_base
    namespace["bids_directory"] = bids_directory

    tutorial_nwbfile_path = bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_ecephys.nwb"
    tutorial_nwbfile = pynwb.read_nwb(path=tutorial_nwbfile_path)
    namespace["tutorial_nwbfile"] = tutorial_nwbfile

    namespace["expected_files"] = expected_files


pytest_collect_file = Sybil(
    parsers=[
        SkipParser(),
        CodeBlockParser(language="bash", evaluator=bash_evaluator),
        PythonCodeBlockParser(),
    ],
    patterns=["tutorials.rst", "conversion_gallery.rst"],
    setup=sybil_setup,
).pytest()
