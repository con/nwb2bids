import json
import pathlib

import nwb2bids


def test_probe_json_includes_optional_fields_when_set(tmp_path: pathlib.Path) -> None:
    """Recommended unit test from review of PR #301."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(probe_name="ProbeA", manufacturer="openephys", description="test probe"),
        ],
        modality="ecephys",
    )

    json_path = tmp_path / "probes.json"
    probe_table.to_json(json_path)

    json_content = json.loads(json_path.read_text())

    expected_content = {
        "description": {"Description": "Probe description from NWB file.", "LongName": "Description"},
        "manufacturer": {
            "Description": "Manufacturer of the probes system (for example, 'openephys', 'alphaomega','blackrock').",
            "LongName": "Manufacturer",
        },
        "probe_name": {
            "Description": "A unique identifier of the probe, can be identical with the device_serial_number.",
            "LongName": "Probe name",
        },
        "type": {"Description": "The type of the probe.", "LongName": "Type"},
    }
    assert json_content == expected_content
