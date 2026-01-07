.. _generate-example-file:

Generating an example NWB file
------------------------------

In case you don't have any NWB files handy, or perhaps you've never worked with NWB files before, you can generate
an example file by running:

.. tabs::
    .. tab:: CLI

        .. code-block:: bash

            nwb2bids tutorial ephys file

    .. tab:: Python Library

        .. code-block:: python

            import nwb2bids

            tutorial_file = nwb2bids.testing.generate_ephys_tutorial(mode="file")


This created an NWB file with contents typical of an extracellular electrophysiology experiment in your home
directory for **nwb2bids**: ``~/nwb2bids_tutorials/ecephys_tutorial_file/ephys.nwb``.

NWB files like these contain a lot of metadata about the probes and electrode structure, which will be useful later
when we compare the source file to the sidecar tables found in BIDS. You can explore these file contents through
`neurosift.app <neurosift.app>`_ by following `this link <https://neurosift.app/nwb?url=https://api.sandbox.dandiarchive.org/api/assets/687b0e17-b3b5-4bbc-8797-3cc2ab4955f5/download/&dandisetId=217739&dandisetVersion=draft>`_.

.. tip::

    The link above actually points to a similar file published on the DANDI Archive, which should be identical to
    what was created on your system. You can explore and visualize your local file contents and structure
    in many other ways, such as the
    `NWB GUIDE <https://nwb-guide.readthedocs.io/en/stable/installation.html>`_,
    `HDFView <https://www.hdfgroup.org/download-hdfview/>`_, or the
    `PyNWB library <https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_read_basics.html#reading-and-exploring-an-nwb-file>`_.

    If you ever upload your own NWB files to DANDI or EMBER, you too can share Neurosift links with your collaborators!



Other modalities
----------------

You can also generate example NWB files for other modalities, such as ``icephys``!

.. tabs::
    .. tab:: CLI

        .. code-block:: bash

            nwb2bids tutorial ephys file --modality icephys

    .. tab:: Python Library

        .. code-block:: python

            import nwb2bids

            tutorial_file = nwb2bids.testing.generate_ephys_tutorial(mode="file", modality="icephys")
