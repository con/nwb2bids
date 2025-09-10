"""Tests for message handling passed to the top-level `converter_nwb_dataset` function."""

import pathlib

import nwb2bids


def test_messages_1(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_1]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionMessage(
            title="Invalid participant ID",
            text=(
                "The participant ID contains underscores; these will be forcibly converted to dashes in the filename "
                "and table references. For consistency, please rename the participants using no spaces or underscores."
            ),
            level=2,
        ),
        nwb2bids.InspectionMessage(
            title="Invalid species", text="Subject species is not a proper Latin binomial or NCBI Taxonomy id.", level=2
        ),
        nwb2bids.InspectionMessage(
            title="Invalid sex", text="Subject sex is not one of the allowed patterns.", level=2
        ),
    ]
    assert messages == expected_messages


def test_messages_2(problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_2]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionMessage(
            title="Invalid participant ID",
            text=(
                "The participant ID contains underscores; these will be forcibly converted to dashes in the filename "
                "and table references. For consistency, please rename the participants using no spaces or underscores."
            ),
            level=2,
        )
    ]
    assert messages == expected_messages
