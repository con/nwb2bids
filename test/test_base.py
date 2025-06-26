import os

import nwb2bids


def test_convert_nwb_dataset(nwb_testdata, tmp_path):
    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata.parent, bids_directory=tmp_path)

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
            }
        else:
            print(root, files, dirs)
            raise


def test_convert_nwb_dataset_with_additional_metadata(nwb_testdata, tmp_path, additional_metadata_fixture):
    nwb2bids.convert_nwb_dataset(
        nwb_directory=nwb_testdata.parent,
        bids_directory=tmp_path,
        additional_metadata_file_path=additional_metadata_fixture,
    )

    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path.name:
            assert dirs == ["sub-12X34"]
            assert set(files) == {
                "participants.json",
                "participants.tsv",
                "dataset_description.json",
            }
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
            }
        else:
            print(root, files, dirs)
            raise


# TODO: Ensure this is valid only if one session per subject.
def test_convert_nwb_dataset_no_session_id(nwb_testdata_no_session_id, tmp_path):
    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata_no_session_id.parent, bids_directory=tmp_path)

    for root, dirs, files in os.walk(tmp_path):
        if root == tmp_path.name:
            assert dirs == ["sub-12X34"]
            assert set(files) == set(["participants.json", "participants.tsv"])
        elif root == os.path.join(tmp_path, "sub-12X34"):
            assert dirs == ["ephys"]
            assert set(files) == set(["sub-12X34_sessions.json", "sub-12X34_sessions.tsv"])
        elif root == os.path.join(tmp_path, "sub-12X34", "ephys"):
            assert dirs == []
            assert set(files) == set(
                [
                    "sub-12X34_channels.tsv",
                    "sub-12X34_ephys.nwb",
                    "sub-12X34_electrodes.tsv",
                    "sub-12X34_probes.tsv",
                ]
            )
        else:
            print(root, files, dirs)
            raise
