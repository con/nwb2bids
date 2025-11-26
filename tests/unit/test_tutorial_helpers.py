import pathlib

import py.path

import nwb2bids


def test_ephys_tutorial_generation(tmpdir: py.path.local):
    tutorial_path = nwb2bids.testing.generate_ephys_tutorial(output_directory=pathlib.Path(tmpdir), mode="file")

    assert tutorial_path.exists()
    assert tutorial_path.suffix == ".nwb"
