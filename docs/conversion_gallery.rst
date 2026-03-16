.. _request-feature: https://github.com/con/nwb2bids/issues/new?title=Support%20more%20additional%20metadata&body=Please%20add%20more%20options%20for%20including%20additional%20metadata%20per%20session.&labels=enhancement



.. _conversion_gallery:

Conversion Gallery
==================

This section provides an in-depth look at how **nwb2bids** extracts metadata from NWB files and organizes it
into BIDS-compliant sidecar files.

For each type of metadata, we'll show:

1. How to express the intended data fields of the NWB neurodata type using PyNWB.
2. What the corresponding extracted BIDS sidecar file contains.

This should help clarify the mapping between NWB and BIDS fields which **nwb2bids** handles.

.. note::

   We'll use the same example data from the :ref:`tutorials` section to demonstrate the fine-grain file contents, so
   be sure to have those files generated before proceeding.



Dataset Description
-------------------

The ``dataset_description.json`` file at the root of the BIDS dataset contains high-level metadata
about the entire dataset. Unless you are converting a dataset that has already been uploaded to DANDI (and thus
may contain several high-level metadata fields not found in any individual files), this information
must be provided via the additional metadata feature (see :ref:`tutorial-additional-metadata`).

A typical ``dataset_description.json`` file might look like:

.. literalinclude:: ./expected_files/dataset_description.json
   :language: json

.. hint::

   If you are using the :meth:`nwb2bids.DatasetConverter.from_remote_dandiset` method, this file should be autopopulated for you with as much metadata as could be inferred from the DANDI API.



Subjects & Sessions
-------------------

In a single NWB file (which can typically represent a single 'session'), subject-level metadata is attached as a
singular ``Subject`` object. In BIDS, information about all subjects in the dataset is collected in the top-level
``participants.tsv`` and ``participants.json`` files, while session-level metadata goes into per-subject
``sessions.tsv`` and ``sessions.json`` sidecar files.

**NWB Session:**

.. code-block:: python

   nwbfile = pynwb.file.NWBFile(
      session_id="A",
      session_start_time=datetime.datetime(1970, 1, 1, tzinfo=dateutil.tz.tzutc()),
      session_description="An example NWB file containing ecephys neurodata types - for use in the nwb2bids tutorials.",
      identifier=uuid.uuid4().hex,
   )

.. invisible-code-block: python

   assert nwbfile.session_id == tutorial_nwbfile.session_id
   assert nwbfile.session_start_time == tutorial_nwbfile.session_start_time, f"{nwbfile.session_start_time} != {tutorial_nwbfile.session_start_time}"
   assert nwbfile.session_description == tutorial_nwbfile.session_description

**NWB Subject:**

.. code-block:: python

   subject = pynwb.file.Subject(
      subject_id="001",
      sex="M",
      species="Mus musculus",
   )
   nwbfile.subject = subject

.. invisible-code-block: python

   assert nwbfile.subject.subject_id == tutorial_nwbfile.subject.subject_id
   assert nwbfile.subject.sex == tutorial_nwbfile.subject.sex
   assert nwbfile.subject.species == tutorial_nwbfile.subject.species

**BIDS Sessions:**

The ``sessions.tsv`` file contains a row for each session of a subject:

.. tsv-table:: ./expected_files/sub-001_sessions.tsv

.. invisible-code-block: python

   test_sessions_tsv_path = bids_directory / "sub-001" / "sub-001_sessions.tsv"
   expected_sessions_tsv_path = expected_files / "sub-001_sessions.tsv"

   test_bytes = test_sessions_tsv_path.read_bytes()
   expected_bytes = expected_sessions_tsv_path.read_bytes()
   assert test_bytes == expected_bytes

**BIDS Participants:**

The ``participants.tsv`` file contains a row for each subject:

.. tsv-table:: ./expected_files/participants.tsv

.. note::

   The column order in all TSV files is strictly enforced by BIDS validation, and **nwb2bids** will make every
   effort to produce valid files based on input data.

.. invisible-code-block: python

   test_participants_tsv_path = bids_directory / "participants.tsv"
   expected_participants_tsv_path = expected_files / "participants.tsv"

   test_bytes = test_participants_tsv_path.read_bytes()
   expected_bytes = expected_participants_tsv_path.read_bytes()
   assert test_bytes == expected_bytes

And the corresponding ``participants.json`` file provides detailed descriptions of each column:

.. literalinclude:: ./expected_files/participants.json
   :language: json

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



General Metadata
----------------

NWB files can contain a number of high-level metadata fields that describe the overall experiment, acquisition parameters, and other details that don't neatly belong to specific neurodata types.
These fields are typically set on the top-level ``pynwb.NWBFile`` object, though there are a few that belong to
particular subfields such as ``pynwb.DeviceModel``.

**NWB file metadata:**

.. code-block:: python

   general_metadata_nwbfile = pynwb.NWBFile(
       session_id="B",
       session_start_time=datetime.datetime(1970, 1, 2, tzinfo=dateutil.tz.tzutc()),
       session_description="An example NWB file used for demonstration of general metadata mapping.",
       identifier=uuid.uuid4().hex,
       institution="My Institution",
       pharmacology="carprofen, 5 mg/kg, given peri-operatively and maintained during recording sessions to manage pain from the craniotomy/implant without sedation.",
       protocol="Mice were placed in a running wheel and allowed to run freely while neural activity was recorded. Mice were trained to stop running in response to air puffs.",
       slices="After the experiment, brains were extracted and sliced into 5 micron sections from primary motor cortex were fixed in epoxy resin for subsequent icephys study.",
   )
   general_metadata_device = pynwb.file.DeviceModel(
       name="GeneralMetadataDevice",
       description="This is an example device used for demonstration of general metadata mapping.",
       manufacturer="imec",
       model_number="NP2014",
   )
   general_metadata_nwbfile.add_device_model(general_metadata_device)

**BIDS general metadata:**

Depending on the modality, the ``ecephys.json`` or ``icephys.json`` file contains metadata such as:

.. tabs::
    .. tab:: Common

        .. code-block:: json

           {
                "InstitutionName": "My Institution",
                "InstitutionAddress": "123 Institution Rd, My City, My State, My Country",
                "InstitutionalDepartmentName": "My Department",
                "PowerLineFrequency": "60",  # In Hz
                "Manufacturer": "imec",
                "ManufacturersModelName": "NP",
                "ManufacturersModelVersion": "2014",
                "RecordingSetupName": "MyLabsRig",
                "SamplingFrequency": 30000.0,  # In Hz
                "DeviceSerialNumber": "ABC123",
                "SoftwareName": "RecordingSoftware",
                "SoftwareVersions": "1.0.0",
                "RecordingDuration": "7200",  # In seconds
                "RecordingType": "continuous",
                "SoftwareFilters": {"Anti-aliasing filter": {"half-amplitude cutoff (Hz)": 500, "Roll-off": "6dB/Octave"}},
                "HardwareFilters": {"Highpass RC filter": {"Half amplitude cutoff (Hz)": 0.0159, "Roll-off": "6dB/Octave"}},
                "BodyPart": "BRAIN",
                "BodyPartDetails": "primary motor cortex",
                "BodyPartDetailsOntology": "http://purl.obolibrary.org/obo/UBERON_0001384"
           }

    .. tab:: _in vivo_

        .. code-block:: json

           {
                "PharmaceuticalName": "carprofen",
                "PharmaceuticalDoseAmount": 5,
                "PharmaceuticalDoseUnits": "mg/kg",
                "PharmaceuticalDoseRegimen": "Given peri-operatively and maintained during recording sessions to manage pain from the craniotomy/implant without sedation.",
                "PharmaceuticalDoseTime": "0",  # In seconds
                "SampleEnvironment": "in-vivo",
                "SupplementarySignals": "Running wheel velocity.",
                "TaskName": "My Running Task",
                "TaskDescription": "Mice were placed in a running wheel and allowed to run freely while neural activity was recorded.",
                "Instructions": "Mice were trained to stop running in response to air puffs."
           }

.. tabs::
    .. tab:: _ex vivo_

        .. code-block:: json

           {
                "SampleEnvironment": "ex-vivo",
                "SampleEmbedding": "Epoxy resin",
                "SliceThickness": "5",  # In microns
                "SampleExtractionProtocol": "Aliquot of primary motor cortex extracted from brain and embedded in epoxy resin."
           }

**Mapping:**

Currently, only one electrical series per NWB file is supported for automated metadata extraction.
Additional sidecar files should be copied and modified to correspond to additional electrical series within the same NWB files.
The use of `acq-[label]` suffixes in the other sidecar filenames is recommended to avoid confusion between series.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - NWB Field
     - BIDS Field
   * - ``nwbfile.institution``
     - ``InstitutionName``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``InstitutionAddress``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``InstitutionalDepartmentName``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PowerLineFrequency``
   * - ``nwbfile.acquisition.electrical_series[0].device_model.manufacturer``
     - ``Manufacturer``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``ManufacturersModelName``
   * - ``nwbfile.acquisition.electrical_series[0].device_model.model_number``
     - ``ManufacturersModelVersion``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``RecordingSetupName``
   * - ``nwbfile.acquisition.electrical_series[0].rate``
     - ``SamplingFrequency``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``DeviceSerialNumber``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SoftwareName``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SoftwareVersions``
   * - ``nwbfile.acquisition.electrical_series[0].data.shape[0] / nwbfile.acquisition.electrical_series[0].rate``
     - ``RecordingDuration``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or comment on `Issue #337 <https://github.com/con/nwb2bids/issues/337>`_
     - ``RecordingType``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``EpochLength``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SoftwareFilters``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``HardwareFilters``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PharmaceuticalName``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PharmaceuticalDoseAmount``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PharmaceuticalDoseUnits``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PharmaceuticalDoseRegimen``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``PharmaceuticalDoseTime``
   * - ``"BRAIN"`` if ``nwbfile.acquisition.electrical_series[0].electrode_group.location is not None``
     - ``BodyPart``
   * - ``nwbfile.acquisition.electrical_series[0].electrode_group.location``
     - ``BodyPartDetails``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or comment on `Issue #338 <https://github.com/con/nwb2bids/issues/338>`_
     - ``BodyPartDetailsOntology``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SampleEnvironment``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SampleEmbedding``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SliceThickness``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SampleExtractionProtocol``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``SupplementarySignals``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``TaskName``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``TaskDescription``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``Instructions``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``CogAtlasID``
   * - | ~Not Yet Implemented~
       | Please directly edit the file(s)
       | or `Request This Feature <request-feature_>`_
     - ``CogPOID``



Ecephys Probes
--------------

In NWB, recording hardware is represented as ``Device`` objects. In the BIDS ``ecephys`` specification,
these become entries in the ``probes.tsv`` and ``probes.json`` sidecar files.

**NWB Device:**

.. code-block:: python

   probe = pynwb.file.Device(
      name="ExampleProbe",
      description="This is an example ecephys probe used for demonstration purposes.",
      manufacturer="`nwb2bids` test suite",
   )

.. invisible-code-block: python

   tutorial_probe = tutorial_nwbfile.devices["ExampleProbe"]

   assert probe.name == tutorial_probe.name
   assert probe.manufacturer == tutorial_probe.manufacturer
   assert probe.description == tutorial_probe.description

**BIDS Probes:**

The ``probes.tsv`` file contains a row for each probe:

.. tsv-table:: ./expected_files/sub-001_ses-A_probes.tsv

.. note::

   The column order in all TSV files is strictly enforced by BIDS validation, and **nwb2bids** will make every
   effort to produce valid files based on input data.

.. invisible-code-block: python

   test_probes_tsv_path = (
      bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_probes.tsv"
   )
   expected_probes_tsv_path = expected_files / "sub-001_ses-A_probes.tsv"

   test_frame = pandas.read_csv(filepath_or_buffer=test_probes_tsv_path, sep="\t")
   expected_frame = pandas.read_csv(filepath_or_buffer=expected_probes_tsv_path, sep="\t")
   pandas.testing.assert_frame_equal(left=test_frame, right=expected_frame)

And the corresponding ``probes.json`` file provides detailed descriptions of each column:

# TODO: fix this

.. code-block:: json

   {}

**Mapping:**

.. container:: table-wrapper

   .. list-table::
      :header-rows: 1

      * - NWB Field
        - BIDS Field
      * - ``Device.name``
        - ``probe_name``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``type``
      * - ``Device.manufacturer``
        - ``manufacturer``
      * - ``Device.description``
        - ``description``



Ecephys Electrodes
------------------

Electrodes represent the physical recording sites on a probe. In classic NWB, these may be stored in the
``electrodes`` table, which requires each electrode to also link to an ``ElectrodeGroup``, commonly interpreted as a
traditional 'shank' in ecephys. In BIDS, they appear in the ``electrodes.tsv`` and ``electrodes.json`` sidecar files.

.. note::

    Certain special probes, such as Neuropixels, may overload the ``electrodes`` table to actually store information about each recording channel. In this case, a special column ``electrode.contact_id`` is used to distinguish physical contacts from recording channels.

**NWB Electrode Table:**

.. code-block:: python

   shank = pynwb.ecephys.ElectrodeGroup(
      name="ExampleShank",
      description="This is an example electrode group (shank) used for demonstration purposes.",
      location="hippocampus",
      device=probe,
   )
   nwbfile.add_electrode_group(shank)

   for _ in range(8):
      nwbfile.add_electrode(
         imp=150_000.0,
         location="hippocampus",
         group=shank,
         filtering="HighpassFilter"
      )

.. invisible-code-block: python

   for index in range(len(tutorial_nwbfile.electrodes)):
      assert nwbfile.electrodes[index]["imp"].values[0] == tutorial_nwbfile.electrodes[index]["imp"].values[0]
      assert nwbfile.electrodes[index]["location"].values[0] == tutorial_nwbfile.electrodes[index]["location"].values[0]
      assert nwbfile.electrodes[index]["group"].values[0].name == tutorial_nwbfile.electrodes[index]["group"].values[0].name

**BIDS Electrodes:**

The ``electrodes.tsv`` file contains a row for each electrode:

.. tsv-table:: ./expected_files/sub-001_ses-A_electrodes.tsv

You may notice many differences between the classic NWB electrode fields and the ``electrodes.tsv`` file. BIDS
requires several fields that NWB does not, but their values may be set to ``n/a`` if they are not known. Additionally,
NWB stores impedance values in units of Ohms, while BIDS expects kOhms - **nwb2bids** handles this conversion automatically.

.. invisible-code-block: python

   test_electrodes_tsv_path = (
      bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_electrodes.tsv"
   )
   expected_electrodes_tsv_path = expected_files / "sub-001_ses-A_electrodes.tsv"

   test_frame = pandas.read_csv(filepath_or_buffer=test_electrodes_tsv_path, sep="\t")
   expected_frame = pandas.read_csv(filepath_or_buffer=expected_electrodes_tsv_path, sep="\t")
   pandas.testing.assert_frame_equal(left=test_frame, right=expected_frame)

And the corresponding ``electrodes.json`` file provides detailed descriptions of each column:

# TODO: fix this

.. code-block:: json

   {}

**Mapping:**

.. container:: table-wrapper

   .. list-table::
      :header-rows: 1

      * - NWB Field (Ecephys)
        - BIDS Field
      * - "e{``electrode.index``}"
        - ``name``
      * - ``electrode.group.device.name``
        - ``probe_name``
      * - ``electrode.x``
        - ``x``
      * - ``electrode.y``
        - ``y``
      * - ``electrode.z``
        - ``z``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``hemisphere``
      * - ``electrode.imp`` (in Ohms)
        - ``impedance`` (in kOhms)
      * - ``electrode.group.name``
        - ``shank_id``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``size``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``electrode_shape``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``material``
      * - ``electrode.location``
        - ``location``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``pipette_solution``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``internal_pipette_diameter``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``external_pipette_diameter``



Ecephys Channels
----------------

Channels represent separate data streams recorded from the physical electrodes. In NWB, this information is often
combined with the previously shown ``electrodes`` table and additional columns may be used to disambiguate physical
contacts from recording channels. In BIDS, channels are described separately from electrodes via the ``channels.tsv``
and ``channels.json`` sidecar files.

**BIDS Channels:**

The ``channels.tsv`` file contains a row for each channel:

.. tsv-table:: ./expected_files/sub-001_ses-A_channels.tsv

You may notice many differences between the classic NWB electrode fields and the ``channels.tsv`` file. In particular,
a number of these values are not specified in the NWB ``electrodes`` table, but are instead set on any data-containing
``ElectricalSeries`` objects that link to those electrodes. In these cases, **nwb2bids** will attempt to find
and extract the relevant values.

.. invisible-code-block: python

   test_channels_tsv_path = (
      bids_directory / "sub-001" / "ses-A" / "ecephys" / "sub-001_ses-A_channels.tsv"
   )
   expected_channels_tsv_path = expected_files / "sub-001_ses-A_channels.tsv"

   test_frame = pandas.read_csv(filepath_or_buffer=test_channels_tsv_path, sep="\t")
   expected_frame = pandas.read_csv(filepath_or_buffer=expected_channels_tsv_path, sep="\t")
   pandas.testing.assert_frame_equal(left=test_frame, right=expected_frame)

And the corresponding ``channels.json`` file provides detailed descriptions of each column:

# TODO: fix this

.. code-block:: json

   {}

**Mapping:**

.. container:: table-wrapper

   .. list-table::
      :header-rows: 1

      * - NWB Field (Ecephys)
        - BIDS Field
      * - ch{``electrode.index``}
        - ``name``
      * - e{``electrode.index``}
        - ``electrode_name``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``type``
      * - ``electrical_series.units`` (if available; fixed to V)
        - ``units``
      * - ``electrical_series.rate`` (if available)
        - ``sampling_frequency``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``low_cutoff``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``high_cutoff``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``reference``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``notch``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``channel_label`` (Good or Bad)
      * - ``electrical_series.name`` (if available)
        - ``stream_id``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``description``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``software_filter_types``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``status``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``status_description``
      * - ``electrical_series.conversion`` (if available)
        - ``gain``
      * - ``electrical_series.starting_time`` (if available)
        - ``time_offset``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``time_reference_channel``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``ground``
      * - | ~Not Yet Implemented~
          | Please directly edit the file(s)
          | or `Request This Feature <request-feature_>`_
        - ``recording_mode``
