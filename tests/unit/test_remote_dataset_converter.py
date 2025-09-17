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
        participant_id="YutaMouse20", species="Mus musculus", sex=None, strain=None
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
