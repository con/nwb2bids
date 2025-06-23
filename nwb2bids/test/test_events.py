from nwb2bids import base
import os


def test_trials_events(nwb_testdata_trials_events, tmp_path):
    tmp_path = str(tmp_path)
    nwb_testdir = os.path.dirname(nwb_testdata_trials_events)
    base.reposit(nwb_testdir, tmp_path)
    # This should be done by invoking the validator once BEP032 is in the BIDS schema:
    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path:
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


def test_epochs_events(nwb_testdata_epochs_events, tmp_path):
    tmp_path = str(tmp_path)
    nwb_testdir = os.path.dirname(nwb_testdata_epochs_events)
    base.reposit(nwb_testdir, tmp_path)
    # This should be done by invoking the validator once BEP032 is in the BIDS schema:
    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path:
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
    tmp_path = str(tmp_path)
    nwb_testdir = os.path.dirname(nwb_testdata_multiple_events)
    base.reposit(nwb_testdir, tmp_path)
    # This should be done by invoking the validator once BEP032 is in the BIDS schema:
    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path:
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
