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
    dataset_converter = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, run_config=run_config)
    assert len(dataset_converter.notifications) == 4

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

    # Check that participants.tsv has participant_id_orig column with original (pre-sanitization) value
    participants_tsv_path = temporary_bids_directory / "participants.tsv"
    participants_tsv_lines = participants_tsv_path.read_text().splitlines()
    assert participants_tsv_lines[0].split("\t")[0] == "participant_id"
    assert participants_tsv_lines[0].split("\t")[1] == "participant_id_orig"
    assert participants_tsv_lines[1].split("\t")[0] == "sub-bad+subject+id"
    assert participants_tsv_lines[1].split("\t")[1] == "sub-bad subject id"

    # Check that sessions.tsv has session_id_orig column with original (pre-sanitization) value
    sessions_tsv_path = temporary_bids_directory / "sub-bad+subject+id" / "sub-bad+subject+id_sessions.tsv"
    sessions_tsv_lines = sessions_tsv_path.read_text().splitlines()
    assert sessions_tsv_lines[0].split("\t")[0] == "session_id"
    assert sessions_tsv_lines[0].split("\t")[1] == "session_id_orig"
    assert sessions_tsv_lines[1].split("\t")[0] == "ses-problematic+2"
    assert sessions_tsv_lines[1].split("\t")[1] == "ses-#problematic!2~"
