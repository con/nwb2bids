import json
import pathlib
import unittest.mock

import nwb2bids
from nwb2bids._tools._probeinterface import _get_probeinterface_term_url


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


def test_get_probeinterface_term_url() -> None:
    """Test that the ProbeInterface term URL is correctly constructed."""
    url = _get_probeinterface_term_url(manufacturer="neuronexus", model="A1x32-Poly3-10mm-50-177")
    expected = (
        "https://raw.githubusercontent.com/SpikeInterface/probeinterface_library/refs/heads/main"
        "/neuronexus/A1x32-Poly3-10mm-50-177/A1x32-Poly3-10mm-50-177.json"
    )
    assert url == expected


def test_probe_json_includes_term_url_when_manufacturer_and_model_set(tmp_path: pathlib.Path) -> None:
    """Test that to_json adds a TermURL in model.Levels when manufacturer and model are set."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(
                probe_name="ProbeA",
                manufacturer="neuronexus",
                model="A1x32-Poly3-10mm-50-177",
                description="test probe",
            ),
        ],
        modality="ecephys",
    )

    json_path = tmp_path / "probes.json"
    probe_table.to_json(json_path)

    json_content = json.loads(json_path.read_text())

    assert "model" in json_content
    assert "Levels" in json_content["model"]
    assert "A1x32-Poly3-10mm-50-177" in json_content["model"]["Levels"]
    assert "TermURL" in json_content["model"]["Levels"]["A1x32-Poly3-10mm-50-177"]
    expected_term_url = (
        "https://raw.githubusercontent.com/SpikeInterface/probeinterface_library/refs/heads/main"
        "/neuronexus/A1x32-Poly3-10mm-50-177/A1x32-Poly3-10mm-50-177.json"
    )
    assert json_content["model"]["Levels"]["A1x32-Poly3-10mm-50-177"]["TermURL"] == expected_term_url


def test_probe_json_no_term_url_when_model_missing(tmp_path: pathlib.Path) -> None:
    """Test that to_json does not add TermURL when no model is set."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(probe_name="ProbeA", manufacturer="openephys", description="test probe"),
        ],
        modality="ecephys",
    )

    json_path = tmp_path / "probes.json"
    probe_table.to_json(json_path)

    json_content = json.loads(json_path.read_text())

    assert "model" not in json_content


def test_write_probe_interface_file_writes_json_for_known_probe(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file fetches and writes the ProbeInterface JSON."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(
                probe_name="ProbeA",
                manufacturer="neuronexus",
                model="A1x32-Poly3-10mm-50-177",
                description="test probe",
            ),
        ],
        modality="ecephys",
    )

    fake_probe_data = {"specification": "probeinterface", "version": "0.2.24", "probes": []}

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    with unittest.mock.patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = unittest.mock.MagicMock()
        mock_response.read.return_value = json.dumps(fake_probe_data).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = unittest.mock.MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        probe_table.write_probe_interface_file(bids_directory=bids_dir)

    expected_output = bids_dir / "probes" / "A1x32-Poly3-10mm-50-177.json"
    assert expected_output.exists()
    written_data = json.loads(expected_output.read_text())
    assert written_data == fake_probe_data


def test_write_probe_interface_file_skips_probe_without_model(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file skips probes that have no model set."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(probe_name="ProbeA", manufacturer="openephys", description="test probe"),
        ],
        modality="ecephys",
    )

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    probe_table.write_probe_interface_file(bids_directory=bids_dir)

    assert not (bids_dir / "probes").exists()


def test_write_probe_interface_file_skips_on_network_error(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file silently skips probes when the library URL is unreachable."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[
            nwb2bids.bids_models.Probe(
                probe_name="ProbeA",
                manufacturer="neuronexus",
                model="A1x32-Poly3-10mm-50-177",
                description="test probe",
            ),
        ],
        modality="ecephys",
    )

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    with unittest.mock.patch("urllib.request.urlopen", side_effect=OSError("network error")):
        probe_table.write_probe_interface_file(bids_directory=bids_dir)

    assert not (bids_dir / "probes").exists()
