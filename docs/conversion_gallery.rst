
.. _conversion_gallery:

Conversion Gallery
==================

This section provides an in-depth look at how **nwb2bids** extracts metadata from NWB files and organizes it
into BIDS-compliant sidecar files. We'll use the same example data from the :ref:`tutorials` section to
demonstrate the fine-grain file contents in line with BEP32 (BIDS Extension Proposal 32 for micro-electrode
electrophysiology).

For each type of metadata, we'll show:

1. How to read the data directly from the NWB file using PyNWB
2. What the corresponding BIDS sidecar file contains
3. The mapping between NWB fields and BIDS fields

This gallery assumes you've already run the tutorial from :ref:`tutorial-single-file` to generate both
the example NWB file and the BIDS dataset.


Setup
-----

First, let's set up our environment and ensure we have the necessary files:

.. code-block:: python

    import pathlib
    import json
    import pandas as pd
    import pynwb

    # Paths to the tutorial data
    tutorial_directory = pathlib.Path.home() / "nwb2bids_tutorials/ecephys_tutorial_file"
    nwb_path = tutorial_directory / "ecephys.nwb"
    bids_directory = tutorial_directory / "bids_dataset_py_1"

.. invisible-code-block: python

    # Ensure the files exist (for doc testing)
    assert nwb_path.exists(), f"NWB file not found at {nwb_path}"
    assert bids_directory.exists(), f"BIDS directory not found at {bids_directory}"


Reading the NWB File
--------------------

Let's open the NWB file and explore its contents:

.. code-block:: python

    # Open the NWB file for reading
    io = pynwb.NWBHDF5IO(str(nwb_path), mode="r")
    nwbfile = io.read()

    # Display basic file information
    print(f"Session ID: {nwbfile.session_id}")
    print(f"Session description: {nwbfile.session_description}")
    print(f"Subject ID: {nwbfile.subject.subject_id}")
    print(f"Species: {nwbfile.subject.species}")
    print(f"Sex: {nwbfile.subject.sex}")

.. invisible-code-block: python

    # Verify the file was opened correctly
    assert nwbfile.session_id == "A"
    assert nwbfile.subject.subject_id == "001"


Probes (Devices)
----------------

In NWB, recording hardware is represented as ``Device`` objects. In the BIDS ``ecephys`` specification,
these become entries in the ``probes.tsv`` and ``probes.json`` sidecar files.

**Reading from NWB:**

.. code-block:: python

    # Access the devices in the NWB file
    for device_name, device in nwbfile.devices.items():
        print(f"Device name: {device_name}")
        print(f"  Description: {device.description}")
        print(f"  Manufacturer: {device.manufacturer}")

.. invisible-code-block: python

    # Verify device data
    assert "ExampleProbe" in nwbfile.devices
    assert nwbfile.devices["ExampleProbe"].manufacturer == "`nwb2bids.testing` module"

**Corresponding BIDS sidecar:**

The BIDS ``probes.tsv`` file contains a row for each probe:

.. code-block:: python

    # Read the BIDS probes.tsv file
    probes_tsv_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_probes.tsv"
    )
    probes_df = pd.read_csv(probes_tsv_path, sep="\t")
    print("\nBIDS probes.tsv:")
    print(probes_df.to_string(index=False))

.. invisible-code-block: python

    # Verify probe data was extracted correctly
    assert len(probes_df) == 1
    assert probes_df.iloc[0]["probe_name"] == "ExampleProbe"

And the corresponding ``probes.json`` file provides detailed descriptions of each column:

.. code-block:: python

    # Read the BIDS probes.json file
    probes_json_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_probes.json"
    )
    with open(probes_json_path, "r") as f:
        probes_metadata = json.load(f)
    
    print("\nBIDS probes.json:")
    print(f"  Metadata keys: {list(probes_metadata.keys())}")
    # Note: The JSON file may be empty ({}) if no additional column descriptions are needed

.. invisible-code-block: python

    # Verify metadata structure
    assert isinstance(probes_metadata, dict)

**Mapping:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - NWB Field
     - BIDS Field
   * - ``Device.name``
     - ``probe_name``
   * - ``Device.description``
     - ``description`` (in JSON)
   * - ``Device.manufacturer``
     - ``manufacturer``


Electrodes
----------

Electrodes represent the individual recording sites on a probe. In NWB, these are stored in the
``electrodes`` table. In BIDS, they appear in the ``electrodes.tsv`` and ``electrodes.json`` files.

**Reading from NWB:**

.. code-block:: python

    # Access the electrodes table
    electrodes_table = nwbfile.electrodes.to_dataframe()
    print(f"\nNWB electrodes table ({len(electrodes_table)} electrodes):")
    print(electrodes_table[["location", "group_name", "imp", "filtering"]].head())

.. invisible-code-block: python

    # Verify electrode data
    assert len(electrodes_table) == 8
    assert electrodes_table["location"].iloc[0] == "hippocampus"

**Corresponding BIDS sidecar:**

.. code-block:: python

    # Read the BIDS electrodes.tsv file
    electrodes_tsv_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.tsv"
    )
    bids_electrodes_df = pd.read_csv(electrodes_tsv_path, sep="\t")
    print("\nBIDS electrodes.tsv (first 5 rows):")
    print(bids_electrodes_df.head().to_string(index=False))

.. invisible-code-block: python

    # Verify electrode extraction
    assert len(bids_electrodes_df) == 8
    assert "name" in bids_electrodes_df.columns
    assert "probe_name" in bids_electrodes_df.columns

The ``electrodes.json`` file provides metadata about the columns:

.. code-block:: python

    # Read the BIDS electrodes.json file
    electrodes_json_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.json"
    )
    with open(electrodes_json_path, "r") as f:
        electrodes_metadata = json.load(f)
    
    print("\nBIDS electrodes.json:")
    print(f"  Metadata keys: {list(electrodes_metadata.keys())}")
    # Note: The JSON file may be empty ({}) if no additional column descriptions are needed

.. invisible-code-block: python

    # Verify metadata structure
    assert isinstance(electrodes_metadata, dict)

**Mapping:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - NWB Field
     - BIDS Field
   * - ``electrodes.id``
     - ``name`` (electrode identifier)
   * - ``electrodes.group.device.name``
     - ``probe_name``
   * - ``electrodes.location``
     - ``location``
   * - ``electrodes.imp``
     - ``impedance`` (in kOhms)
   * - ``electrodes.x``
     - ``x`` (in micrometers)
   * - ``electrodes.y``
     - ``y`` (in micrometers)
   * - ``electrodes.z``
     - ``z`` (in micrometers)
   * - ``electrodes.group.name``
     - ``shank_id``


Channels
--------

Channels represent the data streams recorded from electrodes. In NWB, this information is often distributed
across ``ElectricalSeries`` and the electrodes table. In BIDS, channels are described in ``channels.tsv``
and ``channels.json``.

**Reading from NWB:**

.. code-block:: python

    # Access electrical series (which links to electrodes/channels)
    for name, series in nwbfile.acquisition.items():
        if isinstance(series, pynwb.ecephys.ElectricalSeries):
            print(f"\nElectricalSeries: {name}")
            print(f"  Description: {series.description}")
            print(f"  Sampling rate: {series.rate} Hz")
            print(f"  Number of channels: {series.data.shape[1]}")
            print(f"  Conversion factor: {series.conversion}")
            print(f"  Data shape: {series.data.shape}")

.. invisible-code-block: python

    # Verify electrical series data
    assert "ExampleElectricalSeries" in nwbfile.acquisition
    series = nwbfile.acquisition["ExampleElectricalSeries"]
    assert series.rate == 30000.0
    assert series.data.shape[1] == 8

**Corresponding BIDS sidecar:**

.. code-block:: python

    # Read the BIDS channels.tsv file
    channels_tsv_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.tsv"
    )
    channels_df = pd.read_csv(channels_tsv_path, sep="\t")
    print("\nBIDS channels.tsv (first 5 rows):")
    print(channels_df.head().to_string(index=False))

.. invisible-code-block: python

    # Verify channel extraction
    assert len(channels_df) == 8
    assert "name" in channels_df.columns
    assert "sampling_frequency" in channels_df.columns

The ``channels.json`` file describes the channel metadata:

.. code-block:: python

    # Read the BIDS channels.json file
    channels_json_path = (
        bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.json"
    )
    with open(channels_json_path, "r") as f:
        channels_metadata = json.load(f)
    
    print("\nBIDS channels.json:")
    print(f"  Metadata keys: {list(channels_metadata.keys())}")
    # Note: The JSON file may be empty ({}) if no additional column descriptions are needed

.. invisible-code-block: python

    # Verify metadata structure
    assert isinstance(channels_metadata, dict)

**Mapping:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - NWB Field
     - BIDS Field
   * - ``ElectricalSeries.electrodes``
     - ``electrode_name``
   * - ``ElectricalSeries.rate``
     - ``sampling_frequency``
   * - ``ElectricalSeries.conversion``
     - Used to determine ``units``
   * - ``electrodes.filtering``
     - ``low_cutoff`` / ``high_cutoff``


Subject and Session Information
--------------------------------

Subject-level metadata is stored in the ``participants.tsv`` file, while session-level metadata
goes into the ``sessions.tsv`` file.

**Reading from NWB:**

.. code-block:: python

    # Subject information
    print("\nNWB Subject information:")
    print(f"  Subject ID: {nwbfile.subject.subject_id}")
    print(f"  Species: {nwbfile.subject.species}")
    print(f"  Sex: {nwbfile.subject.sex}")

    # Session information
    print("\nNWB Session information:")
    print(f"  Session ID: {nwbfile.session_id}")
    print(f"  Session description: {nwbfile.session_description}")
    print(f"  Session start time: {nwbfile.session_start_time}")

.. invisible-code-block: python

    # Verify subject and session data
    assert nwbfile.subject.subject_id == "001"
    assert nwbfile.session_id == "A"

**Corresponding BIDS sidecar:**

.. code-block:: python

    # Read the BIDS participants.tsv file
    participants_tsv_path = bids_directory / "participants.tsv"
    participants_df = pd.read_csv(participants_tsv_path, sep="\t")
    print("\nBIDS participants.tsv:")
    print(participants_df.to_string(index=False))

.. invisible-code-block: python

    # Verify participants data
    assert len(participants_df) == 1
    assert participants_df.iloc[0]["participant_id"] == "sub-001"

.. code-block:: python

    # Read the BIDS sessions.tsv file
    sessions_tsv_path = bids_directory / "sub-001" / "sub-001_sessions.tsv"
    sessions_df = pd.read_csv(sessions_tsv_path, sep="\t")
    print("\nBIDS sessions.tsv:")
    print(sessions_df.to_string(index=False))

.. invisible-code-block: python

    # Verify sessions data
    assert len(sessions_df) == 1
    assert sessions_df.iloc[0]["session_id"] == "ses-A"

**Mapping:**

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - NWB Field
     - BIDS Field
   * - ``subject.subject_id``
     - ``participant_id`` (with ``sub-`` prefix)
   * - ``subject.species``
     - ``species``
   * - ``subject.sex``
     - ``sex``
   * - ``session_id``
     - ``session_id`` (with ``ses-`` prefix)
   * - ``session_start_time``
     - ``acq_time``


Dataset Description
-------------------

The ``dataset_description.json`` file at the root of the BIDS dataset contains high-level metadata
about the entire dataset.

.. code-block:: python

    # Read the BIDS dataset_description.json file
    dataset_desc_path = bids_directory / "dataset_description.json"
    with open(dataset_desc_path, "r") as f:
        dataset_description = json.load(f)
    
    print("\nBIDS dataset_description.json:")
    for key, value in dataset_description.items():
        print(f"  {key}: {value}")

.. invisible-code-block: python

    # Verify dataset description
    assert "Name" in dataset_description
    assert "BIDSVersion" in dataset_description
    # BIDSVersion is set by the tool to the current supported BIDS version

This file can be augmented with additional metadata using the ``--additional-metadata-file-path`` option
as shown in :ref:`tutorial-additional-metadata`.


Cleanup
-------

Don't forget to close the NWB file when you're done:

.. code-block:: python

    # Close the NWB file
    io.close()

.. invisible-code-block: python

    # The file is now closed and should not be used further
    pass


Summary
-------

This conversion gallery demonstrated how **nwb2bids** extracts rich metadata from NWB files and
organizes it according to the BIDS BEP32 specification for electrophysiology data. The key benefits
of this approach include:

* **Standardization**: BIDS provides a consistent structure that makes data easier to share and analyze
* **Discoverability**: Sidecar TSV and JSON files make metadata human-readable and machine-accessible
* **Interoperability**: BIDS-formatted datasets can be used with a wide range of analysis tools

For more complex examples including multiple sessions, different modalities (icephys), and customization
options, see the :ref:`tutorials` section.


Additional Resources
--------------------

* `BEP32 Specification <https://github.com/bids-standard/bids-specification/pull/1705>`_: The BIDS Extension
  Proposal for micro-electrode electrophysiology
* `NWB Electrophysiology Tutorial <https://pynwb.readthedocs.io/en/stable/tutorials/domain/ecephys.html>`_:
  PyNWB tutorial on working with electrophysiology data
* `BIDS Specification <https://bids-specification.readthedocs.io/>`_: The complete BIDS specification
