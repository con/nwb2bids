import pathlib

import py.path

import nwb2bids


def test_convert_nwb_dataset(nwb_testdata: pathlib.Path, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata.parent, bids_directory=tmpdir)

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
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=tmpdir, expected_structure=expected_structure)


def test_convert_nwb_dataset_with_additional_metadata(
    nwb_testdata: pathlib.Path, tmpdir: py.path.local, additional_metadata_fixture: pathlib.Path
):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(
        nwb_directory=nwb_testdata.parent,
        bids_directory=tmpdir,
        additional_metadata_file_path=additional_metadata_fixture,
    )

    expected_structure = {
        tmpdir: {
            "directories": {"sub-12X34"},
            "files": {"participants.json", "participants.tsv", "dataset_description.json"},
        },
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
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=tmpdir, expected_structure=expected_structure)


def test_convert_nwb_dataset_no_session_id(nwb_testdata_no_session_id: pathlib.Path, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_testdata_no_session_id.parent, bids_directory=tmpdir)

    expected_structure = {
        tmpdir: {"directories": {"sub-12X34"}, "files": {"participants.json", "participants.tsv"}},
        tmpdir
        / "sub-12X34": {
            "directories": {"ephys"},
            "files": {"sub-12X34_sessions.json", "sub-12X34_sessions.tsv"},
        },
        tmpdir
        / "sub-12X34"
        / "ephys": {
            "directories": set(),
            "files": {
                "sub-12X34_channels.tsv",
                "sub-12X34_ephys.nwb",
                "sub-12X34_electrodes.tsv",
                "sub-12X34_probes.tsv",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=tmpdir, expected_structure=expected_structure)
