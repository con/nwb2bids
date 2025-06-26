import os
import pathlib

import py.path

import nwb2bids


def test_trials_events(nwb_testdata_trials_events, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata_trials_events.parent, bids_directory=tmpdir)

    expected_structure = {
        tmpdir: {"directories": {"sub-12X34"}, "files": {"participants.json", "participants.tsv"}},
        tmpdir
        / "sub-12X34": {
            "directories": {"ses-20240309"},
            "files": {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"},
        },
        tmpdir
        / "sub-12X34"
        / "ses-20240309": {
            "directories": {"ephys"},
            "files": set(),
        },
        tmpdir
        / "sub-12X34"
        / "ses-20240309"
        / "ephys": {
            "directories": set(),
            "files": {
                "sub-12X34_ses-20240309_channels.tsv",
                "sub-12X34_ses-20240309_electrodes.tsv",
                "sub-12X34_ses-20240309_ephys.nwb",
                "sub-12X34_ses-20240309_probes.tsv",
                "sub-12X34_ses-20240309_events.tsv",
                "sub-12X34_ses-20240309_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=tmpdir, expected_structure=expected_structure)


def test_epochs_events(nwb_testdata_epochs_events, tmp_path):
    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata_epochs_events.parent, bids_directory=tmp_path)

    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path.name:
            assert dirs == ["sub-12X34"]
            assert set(files) == {"participants.json", "participants.tsv"}
        elif root == os.path.join(tmp_path, "sub-12X34"):
            assert dirs == ["ses-20240309"]
            assert set(files) == {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"}
        elif root == os.path.join(tmp_path, "sub-12X34", "ses-20240309"):
            assert dirs == ["ephys"]
            assert files == []
        elif root == os.path.join(tmp_path, "sub-12X34", "ses-20240309", "ephys"):
            assert dirs == []
            assert set(files) == {
                "sub-12X34_ses-20240309_channels.tsv",
                "sub-12X34_ses-20240309_electrodes.tsv",
                "sub-12X34_ses-20240309_ephys.nwb",
                "sub-12X34_ses-20240309_probes.tsv",
                "sub-12X34_ses-20240309_events.tsv",
                "sub-12X34_ses-20240309_events.json",
            }
        else:
            print(root, files, dirs)
            raise


def test_multiple_events(nwb_testdata_multiple_events, tmp_path):
    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata_multiple_events.parent, bids_directory=tmp_path)

    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path.name:
            assert dirs == ["sub-12X34"]
            assert set(files) == {"participants.json", "participants.tsv"}
        elif root == os.path.join(tmp_path, "sub-12X34"):
            assert dirs == ["ses-20240309"]
            assert set(files) == {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"}
        elif root == os.path.join(tmp_path, "sub-12X34", "ses-20240309"):
            assert dirs == ["ephys"]
            assert files == []
        elif root == os.path.join(tmp_path, "sub-12X34", "ses-20240309", "ephys"):
            assert dirs == []
            assert set(files) == {
                "sub-12X34_ses-20240309_channels.tsv",
                "sub-12X34_ses-20240309_electrodes.tsv",
                "sub-12X34_ses-20240309_ephys.nwb",
                "sub-12X34_ses-20240309_probes.tsv",
                "sub-12X34_ses-20240309_events.tsv",
                "sub-12X34_ses-20240309_events.json",
            }
        else:
            print(root, files, dirs)
            raise
