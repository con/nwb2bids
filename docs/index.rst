.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   user_guide
   tutorials
   conversion_gallery
   developer_guide
   api/index

.. image:: assets/nwb2bids-color.svg
   :alt: nwb2bids logo
   :align: center
   :width: 200px
   :target: #

nwb2bids
========

**nwb2bids** reorganizes NWB files into a BIDS directory layout.

Features:

* Automatically renames NWB files and their directories to conform to BIDS conventions.
* Extracts relevant metadata from NWB files to populate BIDS sidecar TSV & JSON files.
* Currently supports `BEP32 <https://github.com/bids-standard/bids-specification/pull/1705>`_ (micro-electrode electrophysiology) data types, such as extracellular (``ecephys``) and intracellular (``icephys``) electrophysiology, as well as associated behavioral events.

In the future, we plan to support:

* stimuli
* videos
* ``ndx-events``
* Hierarchical Event Descriptors (HED)
* microscopy
* ``ndx-pose`` + BIDS motion
* eye tracking



Installation
------------

To install the latest stable release of **nwb2bids** you can use either `pip <https://pip.pypa.io/>`_ or `conda <https://docs.conda.io/projects/conda/en/stable/user-guide/getting-started.html>`_.

To do this, run:

.. tabs::

   .. tab:: pip

      .. code-block:: bash

         pip install nwb2bids

   .. tab:: conda-forge

      .. code-block:: bash

         conda install -c conda-forge nwb2bids

Some extra optional dependencies include the ability to run remotely on a dataset hosted on `DANDI
<https://dandiarchive.org/>`_.

The easiest way to install these extras is to run:

.. tabs::

   .. tab:: pip

      .. code-block:: bash

         pip install "nwb2bids[dandi]"


How to use the documentation
----------------------------

Our documentation is structured to cater to users ranging from beginners to advanced developers and contributors. Below is an overview of the key sections to help you navigate our documentation effectively

* **User Guide**

  The :ref:`User Guide <user_guide>` offers a comprehensive overview of our data models and core functionalities.
  It is recommended for users who wish to understand the underlying concepts and extend their scripts beyond basic conversions.

* **Developer Guide**

  For developers interested in contributing to **nwb2bids**, the :ref:`Developer Guide <developer_guide>` provides essential information such as instructions for building your own classes,  our coding style, instructions on how to build the documentation, run the testing suite, etc.

* **API Reference**

  Detailed documentation of the **nwb2bids** API can be found in the :ref:`API <api>` section.


Do you find that some information is missing or some section lacking or unclear? Reach out with an issue or pull request on our `GitHub repository <https://github.com/catalystneuro/neuroconv>`_.
We are happy to help and appreciate your feedback.



Data Standards and Related Resources
------------------------------------

Understanding the Standardization Landscape
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**nwb2bids** operates at the intersection of multiple neuroscience data standards.
This section clarifies which standards are currently supported, which are planned for future implementation, and how they relate to the broader standardization ecosystem.

For a comprehensive overview of neuroscience data standards and their relationships, see the `SfN 2025: "The Ecosystem of Standards in Neuroscience: Which Ones Are For You?" Poster <https://doi.org/10.5281/zenodo.18333007>`_ by Oliver Contier et al.

Currently Supported Standards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**nwb2bids** currently provides full support for:

* **NWB (Neurodata Without Borders)**: A data standard for neurophysiology that provides a common format for cellular-based neurophysiology data, along with trial structure, metadata, and behavioral data.
  **nwb2bids** reads and processes NWB files as input.

  - `NWB Format Specification <https://nwb-schema.readthedocs.io/en/latest/>`_: Technical specification of the NWB format
  - `NWB Overview <https://nwb-overview.readthedocs.io/en/latest/>`_: High-level overview of NWB and its ecosystem
  - `NWB Extensions <https://nwb-extensions.github.io/>`_: Catalog of community-developed extensions (NDX) that extend NWB for specific data types and use cases

* **BIDS (Brain Imaging Data Structure)**: A specification for organizing neuroscience data in a standardized directory structure with accompanying metadata.
  **nwb2bids** outputs data organized according to BIDS conventions.

  - `BIDS Specification <https://bids.neuroimaging.io/>`_: Official BIDS specification
  - `BIDS Extension Proposals (BEPs) <https://bids.neuroimaging.io/extensions/beps.html>`_: Overview of ongoing extensions to BIDS for additional modalities (eye tracking, microscopy, etc.).
    Note that this page evolves as new extensions are proposed and adopted.
  - **BEP32 (BIDS Extension Proposal 32)**: Currently supported for micro-electrode electrophysiology, including extracellular (``ecephys``) and intracellular (``icephys``) electrophysiology, as well as associated behavioral events.
    See the `BEP32 pull request <https://github.com/bids-standard/bids-specification/pull/1705>`_ for specification details.

* **HED (Hierarchical Event Descriptors)** (`hedtags.org <https://www.hedtags.org/>`_): Basic support for annotating events and experimental structure with standardized vocabularies.
  **nwb2bids** currently includes HED version specification (v8.3.0) in dataset metadata and automatically assigns basic HED tags to event tables (e.g., "Experimental-trial" for trials, "Time-block" for epochs).
  Future work will extend HED annotation capabilities.

Planned Future Support
~~~~~~~~~~~~~~~~~~~~~~

We are actively planning to extend **nwb2bids** support to include:

* `ndx-events <https://github.com/rly/ndx-events>`_: NWB extension for representing timestamped event and TTL pulse data
* `ndx-pose <https://github.com/rly/ndx-pose>`_ + `BIDS motion <https://bids-specification.readthedocs.io/en/stable/modality-specific-files/motion.html>`_: For pose estimation and motion capture data
* Additional data modalities: stimuli, videos, `microscopy (BEP031) <https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.871228/full>`_, and `eye tracking (BEP020) <https://bids.neuroimaging.io/extensions/beps/bep_020.html>`_
* Extended HED annotation capabilities beyond basic tagging

These extensions will require integration with their respective standards and may depend on external tooling or additional NWB extensions.

Related Standardization Efforts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**nwb2bids** operates in the broader context of neuroscience data standardization initiatives:

* `DICOM <https://www.dicomstandard.org/>`_ `WG-32: Neurophysiology Data <https://www.dicomstandard.org/activity/wgs/wg-32>`_: The Digital Imaging and Communications in Medicine (DICOM) working group focused on standardizing neurophysiology data, including EEG, EMG, evoked potentials, and other clinical neurophysiology signals.
  While DICOM and NWB/BIDS serve different use cases and communities, awareness of parallel standardization efforts helps users understand the broader landscape of neurophysiology data standards.

Related Tools and Converters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**nwb2bids** is part of a broader ecosystem of tools for working with NWB and BIDS data:

**NWB Converters:**

- `NWB Guide <https://nwb-guide.readthedocs.io/en/latest/>`_: A no-code graphical interface for converting data to NWB format

- `NeuroConv <https://neuroconv.readthedocs.io/en/latest/>`_: A Python library providing low-code conversion pipelines to NWB format from various proprietary and open formats

**BIDS Converters for Other Modalities:**

- `BIDS Converters <https://bids.neuroimaging.io/tools/converters.html>`_: Collection of converters for different neuroimaging and neuroscience data modalities (MRI, EEG, MEG, iEEG, PET, and more)

**AI Assistants for Standards:**

- `qp - AI Assistants Collection <https://github.com/magland/qp>`_: A curated collection of AI assistants for various neuroscience projects and data standards, providing interactive help with BIDS, NWB, and related tools
