"""Unit tests for the `DatasetConverter` class and its methods."""

import pathlib

import numpy
import pydantic
import pytest

import nwb2bids


@pytest.mark.remote
def test_remote_dataset_converter_initialization(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(
        dandiset_id="000003", limit=2, run_config=run_config
    )

    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)


@pytest.mark.remote
def test_remote_dataset_converter_metadata_extraction(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(
        dandiset_id="000003", limit=2, run_config=run_config
    )
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
                probe_name="Implant", type=None, description="Silicon electrodes on Intan probe.", manufacturer=None
            )
        ]
    )

    assert session_metadata.channel_table is not None
    assert len(session_metadata.channel_table.channels) == 65
    assert session_metadata.channel_table.channels[0] == nwb2bids.bids_models.Channel(
        channel_name="ch0", reference="0", type="N/A", unit="V", hardware_filters="none", software_filters="N/A"
    )

    assert session_metadata.electrode_table is not None
    assert len(session_metadata.channel_table.channels) == 65
    assert session_metadata.electrode_table.electrodes[0] == nwb2bids.bids_models.Electrode(
        name="e000",
        probe_name="Implant",
        hemisphere="N/A",
        x=numpy.nan,
        y=numpy.nan,
        z=numpy.nan,
        impedance=-0.001,
        shank_id="shank1",
        location="unknown",
    )


@pytest.mark.remote
def test_remote_dataset_converter_initialization_on_invalid_metadata(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)
    dataset_converter = nwb2bids.DatasetConverter.from_remote_dandiset(
        dandiset_id="000005", limit=2, run_config=run_config
    )

    assert isinstance(dataset_converter, nwb2bids.DatasetConverter)
    assert len(dataset_converter.messages) == 1
    assert dataset_converter.messages[0] == nwb2bids.InspectionResult(
        title="INFO: invalid Dandiset metadata",
        reason="This Dandiset has invalid metadata.",
        solution="Required dataset description fields are inferred from the raw metadata instead.",
        category=nwb2bids.Category.INTERNAL_ERROR,
        severity=nwb2bids.Severity.INFO,
    )

    assert dataset_converter.dataset_description == nwb2bids.bids_models.DatasetDescription(
        Name="Electrophysiology data from thalamic and cortical neurons during somatosensation",
        BIDSVersion="1.10",
        Description=(
            "intracellular and extracellular electrophysiology recordings performed on mouse barrel cortex and "
            "ventral posterolateral nucleus (vpm) in whisker-based object locating task."
        ),
        DatasetType="raw",
        Authors=["Yu, Jianing", "Gutnisky, Diego A", "Hires, S Andrew", "Svoboda, Karel"],
        License="CC-BY-4.0",
    )
