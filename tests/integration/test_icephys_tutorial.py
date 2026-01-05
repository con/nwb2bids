import pathlib

import py

import nwb2bids


def test_icephys_tutorial_file(tmpdir: py.path.local, temporary_bids_directory: pathlib.Path):
    tutorial_path = nwb2bids.testing.generate_ephys_tutorial(
        output_directory=pathlib.Path(tmpdir), mode="file", modality="icephys"
    )

    nwb_paths = [tutorial_path]
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert not any(converter.messages)
