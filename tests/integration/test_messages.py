"""Tests for message handling passed to the top-level `converter_nwb_dataset` function."""

import pathlib

import nwb2bids


def test_messages_1(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [minimal_nwbfile_path.parent]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)
    assert messages is not None
