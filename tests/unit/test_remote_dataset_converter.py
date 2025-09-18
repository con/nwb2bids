"""Unit tests for the `DatasetConverter` class and its methods."""

import pathlib

import pydantic
import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_dataset_converter_initialization(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003", limit=2)
    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)


@pytest.mark.remote
def test_remote_dataset_converter_metadata_extraction(temporary_bids_directory: pathlib.Path):
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(dandiset_id="000003", limit=2)
    dataset_converter.extract_metadata()

    assert len(dataset_converter.session_converters) == 2

    session_converter = dataset_converter.session_converters[0]
    assert session_converter.session_id == "YutaMouse20-140321"
    assert session_converter.nwbfile_paths == [
        pydantic.HttpUrl("https://dandiarchive.s3.amazonaws.com/blobs/bb8/1f7/bb81f7b3-4cfa-40e7-aa89-95beb1954d8c")
    ]

    session_metadata = session_converter.session_metadata
    assert session_metadata.participant == nwb2bids.bids_models.Participant(
        messages=[
            nwb2bids.InspectionResult(
                title="Missing participant sex",
                reason="Archives such as DANDI or EMBER require the subject sex to be specified.",
                solution=(
                    "Specify the `sex` field of the Subject object attached to the NWB file as one of four options: "
                    '"M" (for male), "F" (for female), "U" (for unknown), or "O" (for other).\nNOTE: for certain '
                    'animal species with more specific genetic determinants, such as C elegans, use "O" (for other) '
                    'then further specify the subtypes using other custom fields. For example, `c_elegans_sex="XO"`'
                ),
                examples=None,
                field="nwbfile.subject.sex",
                source_file_paths=None,
                target_file_paths=None,
                data_standards=[nwb2bids.DataStandard.DANDI],
                category=nwb2bids.Category.SCHEMA_INVALIDATION,
                severity=nwb2bids.Severity.CRITICAL,
            ),
            nwb2bids.InspectionResult(
                title="Invalid session ID",
                reason=(
                    "The session ID contains invalid characters. BIDS allows only dashes to be used as separators in "
                    "session entity label. Underscores, spaces, slashes, and special characters (including #) are "
                    "expressly forbidden."
                ),
                solution="Rename the session without using spaces or underscores.",
                examples=["`ses_01` -> `ses-01`", "`session #2` -> `session-2`", "`id 2 from 9/1/25` -> `id-2-9-1-25`"],
                field="nwbfile.session_id",
                source_file_paths=[
                    pydantic.HttpUrl(
                        "https://dandiarchive.s3.amazonaws.com/blobs/bb8/1f7/bb81f7b3-4cfa-40e7-aa89-95beb1954d8c"
                    )
                ],
                target_file_paths=None,
                data_standards=[nwb2bids.DataStandard.BIDS, nwb2bids.DataStandard.DANDI],
                category=nwb2bids.Category.STYLE_SUGGESTION,
                severity=nwb2bids.Severity.ERROR,
            ),
        ],
        participant_id="YutaMouse20",
        species="Mus musculus",
        sex=None,
        strain=None,
    )
    assert session_metadata.events is None

    assert session_metadata.probe_table == nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(
                probe_id="Implant", type=None, description="Silicon electrodes on Intan probe.", manufacturer=None
            )
        ]
    )

    assert session_metadata.channel_table is not None
    assert len(session_metadata.channel_table.channels) == 65
    assert session_metadata.channel_table.channels[0] == nwb2bids.bids_models.Channel(
        channel_id="0", electrode_id="0", type="EXT", unit="V", sampling_frequency=None, gain=None
    )

    assert session_metadata.electrode_table is not None
    assert len(session_metadata.channel_table.channels) == 65
    assert session_metadata.electrode_table.electrodes[0] == nwb2bids.bids_models.Electrode(
        electrode_id=0, probe_id="Implant", location="unknown"
    )
