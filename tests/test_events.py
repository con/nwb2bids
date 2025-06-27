import pathlib

import py.path

import nwb2bids


def test_trials_events(nwb_file_with_trials_events: pathlib.Path, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_file_with_trials_events.parent, bids_directory=tmpdir)

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


def test_epochs_events(nwb_file_with_epochs_events: pathlib.Path, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_file_with_epochs_events.parent, bids_directory=tmpdir)

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


def test_multiple_events(nwb_file_with_multiple_events: pathlib.Path, tmpdir: py.path.local):
    tmpdir = pathlib.Path(tmpdir)

    nwb2bids.convert_nwb_dataset(nwb_directory=nwb_file_with_multiple_events.parent, bids_directory=tmpdir)

    expected_structure = {
        tmpdir: {"directories": {"sub-subject"}, "files": {"participants.json", "participants.tsv"}},
        tmpdir
        / "sub-subject": {
            "directories": {"ses-20240309"},
            "files": {"sub-subject_sessions.json", "sub-subject_sessions.tsv"},
        },
        tmpdir
        / "sub-subject"
        / "ses-20240309": {
            "directories": {"ephys"},
            "files": set(),
        },
        tmpdir
        / "sub-subject"
        / "ses-20240309"
        / "ephys": {
            "directories": set(),
            "files": {
                "sub-subject_ses-20240309_channels.tsv",
                "sub-subject_ses-20240309_electrodes.tsv",
                "sub-subject_ses-20240309_ephys.nwb",
                "sub-subject_ses-20240309_probes.tsv",
                "sub-subject_ses-20240309_events.tsv",
                "sub-subject_ses-20240309_events.json",
            },
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=tmpdir, expected_structure=expected_structure)
