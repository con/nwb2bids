"""Sanitization tests for the API."""

import pathlib

import nwb2bids


def test_convert_nwb_dataset_basic_sanitization(
    problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    nwb_paths = [problematic_nwbfile_path_2]
    run_config = nwb2bids.RunConfig(
        bids_directory=temporary_bids_directory,
        sanitization_config=nwb2bids.sanitization.SanitizationConfig(sub_labels=True, ses_labels=True),
    )
    converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)

    assert len(converter.messages) == 4
    expected_structure = {
        temporary_bids_directory: {
            "directories": {"sub-bad+subject+id"},
            "files": {"dataset_description.json", "participants.json", "participants.tsv"},
        },
        temporary_bids_directory
        / "sub-bad+subject+id": {
            "directories": {"ses-problematic+2"},
            "files": {"sub-bad+subject+id_sessions.json", "sub-bad+subject+id_sessions.tsv"},
        },
        temporary_bids_directory
        / "sub-bad+subject+id"
        / "ses-problematic+2": {
            "directories": {"ecephys"},
            "files": set(),
        },
        temporary_bids_directory
        / "sub-bad+subject+id"
        / "ses-problematic+2"
        / "ecephys": {
            "directories": set(),
            "files": {
                "sub-bad+subject+id_ses-problematic+2_ecephys.nwb",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(
        directory=temporary_bids_directory, expected_structure=expected_structure
    )
