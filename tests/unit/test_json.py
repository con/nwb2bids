import json
import pathlib
import unittest.mock

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


def test_probe_json_no_term_url_by_default(tmp_path: pathlib.Path) -> None:
    """Test that to_json does not add TermURL when no probe_term_url is provided."""
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
    assert "Levels" not in json_content["model"]


def test_probe_json_includes_term_url_when_probe_flag_provided(tmp_path: pathlib.Path) -> None:
    """Test that to_json adds TermURL under model.Levels when probe_term_url and probe_model_name are given."""
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

    expected_term_url = (
        "https://raw.githubusercontent.com/SpikeInterface/probeinterface_library/refs/heads/main"
        "/neuronexus/A1x32-Poly3-10mm-50-177/A1x32-Poly3-10mm-50-177.json"
    )
    json_path = tmp_path / "probes.json"
    probe_table.to_json(json_path, probe_term_url=expected_term_url, probe_model_name="A1x32-Poly3-10mm-50-177")

    json_content = json.loads(json_path.read_text())

    assert "model" in json_content
    assert "Levels" in json_content["model"]
    assert "A1x32-Poly3-10mm-50-177" in json_content["model"]["Levels"]
    assert json_content["model"]["Levels"]["A1x32-Poly3-10mm-50-177"]["TermURL"] == expected_term_url


def test_write_probe_interface_file_writes_json_for_known_probe(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file fetches and writes the ProbeInterface JSON."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[nwb2bids.bids_models.Probe(probe_name="ProbeA", description="test probe")],
        modality="ecephys",
    )

    fake_probe_data = {"specification": "probeinterface", "version": "0.2.24", "probes": []}

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    with unittest.mock.patch("requests.get") as mock_get:
        mock_response = unittest.mock.MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = fake_probe_data
        mock_get.return_value = mock_response

        term_url, model_name = probe_table.write_probe_interface_file(
            bids_directory=bids_dir, probe_name="neuronexus/A1x32-Poly3-10mm-50-177"
        )

    expected_output = bids_dir / "probes" / "A1x32-Poly3-10mm-50-177.json"
    assert expected_output.exists()
    written_data = json.loads(expected_output.read_text())
    assert written_data == fake_probe_data

    expected_term_url = (
        "https://raw.githubusercontent.com/SpikeInterface/probeinterface_library/refs/heads/main"
        "/neuronexus/A1x32-Poly3-10mm-50-177/A1x32-Poly3-10mm-50-177.json"
    )
    assert term_url == expected_term_url
    assert model_name == "A1x32-Poly3-10mm-50-177"
    assert probe_table.probes[0].model == "A1x32-Poly3-10mm-50-177"


def test_write_probe_interface_file_invalid_probe_name_adds_notification(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file adds a ProbeNotFound notification for an invalid probe name."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[nwb2bids.bids_models.Probe(probe_name="ProbeA", description="test probe")],
        modality="ecephys",
    )

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    term_url, model_name = probe_table.write_probe_interface_file(bids_directory=bids_dir, probe_name="no-slash-here")

    assert term_url is None
    assert model_name is None
    assert not (bids_dir / "probes").exists()
    assert any(n.identifier == "ProbeNotFound" for n in probe_table.notifications)


def test_write_probe_interface_file_not_found_adds_notification(tmp_path: pathlib.Path) -> None:
    """Test that write_probe_interface_file adds a ProbeNotFound notification when the library returns 404."""
    probe_table = nwb2bids.bids_models.ProbeTable(
        probes=[nwb2bids.bids_models.Probe(probe_name="ProbeA", description="test probe")],
        modality="ecephys",
    )

    bids_dir = tmp_path / "bids_output"
    bids_dir.mkdir()

    with unittest.mock.patch("requests.get") as mock_get:
        mock_response = unittest.mock.MagicMock()
        mock_response.ok = False
        mock_get.return_value = mock_response

        term_url, model_name = probe_table.write_probe_interface_file(
            bids_directory=bids_dir, probe_name="neuronexus/A1x32-Poly3-10mm-50-177"
        )

    assert term_url is None
    assert model_name is None
    assert not (bids_dir / "probes").exists()
    assert any(n.identifier == "ProbeNotFound" for n in probe_table.notifications)
