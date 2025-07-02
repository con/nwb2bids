import pathlib

import nwb2bids


def test_session_converter_initialization(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)

    assert isinstance(session_converters, list)
    assert len(session_converters) == 1
    assert isinstance(session_converters[0], nwb2bids.SessionConverter)


def test_session_converter_metadata_extraction(
    minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path
):
    session_converters = nwb2bids.SessionConverter.from_nwb_directory(nwb_directory=minimal_nwbfile_path.parent)
    session_converters[0].extract_session_metadata()

    expected_session_metadata = nwb2bids.models.BidsSessionMetadata(
        session_id="20240309",
        subject=nwb2bids.models.Subject(participant_id="123", species="Mus musculus", sex="male"),
        extra={
            "session": {"session_id": "20240309", "number_of_trials": None, "comments": "session_description"},
            "general_ephys": {"InstitutionName": None},
            "subject": {"participant_id": "123", "species": "Mus musculus", "strain": None, "sex": "male"},
            "probes": [],
        },
    )
    assert session_converters[0].session_metadata == expected_session_metadata
