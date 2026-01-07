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
    assert not any(converter.notifications)

    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-001"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-001": {
            "directories": {"ses-A"},
            "files": {"sub-001_sessions.json", "sub-001_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-001"
        / "ses-A": {
            "directories": {"icephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-001"
        / "ses-A"
        / "icephys": {
            "directories": set(),
            "files": {
                "sub-001_ses-A_icephys.nwb",
                "sub-001_ses-A_probes.json",
                "sub-001_ses-A_probes.tsv",
                "sub-001_ses-A_electrodes.json",
                "sub-001_ses-A_electrodes.tsv",
                "sub-001_ses-A_channels.json",
                "sub-001_ses-A_channels.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
