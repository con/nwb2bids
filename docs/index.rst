
.. image:: assets/nwb2bids-color.svg
   :width: 300

..
  :scale: 100 %
  :align: center

nwb2bids
========

**nwb2bids** reorganizes NWB files into a BIDS directory layout.

Features:

* Automatically renames NWB files and their directories to conform to BIDS conventions.
* Extracts relevant metadata from NWB files to populate BIDS sidecar TSV & JSON files.
* Currently supports `BEP32 <https://github.com/bids-standard/bids-specification/pull/1705>`_ (micro-electrode electrophysiology) data types, such as extracellular (ecephys) and intracellular (icephys) electrophysiology, as well as associated behavioral events.

In the future, we plan to support:

* stimuli
* videos
* ndx-events
* HED
* microscopy
* pose + motion
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

Our documentation is structured to cater to users ranging from beginners to advanced developers and contributors.
Below is an overview of the key sections to help you navigate our documentation effectively

* **Getting Started: Conversion Examples Gallery**

  If you're new to NeuroConv or NWB, start with the :ref:`Conversion Examples Gallery <conversion_gallery>`.
  This section provides concise scripts for converting data from common formats (e.g., Blackrock, Plexon, Neuralynx) to NWB. It's designed to get you up and running quickly.

* **User Guide**

  The :ref:`User Guide <user_guide>` offers a comprehensive overview of NeuroConv's data model and functionalities.
  It is recommended for users who wish to understand the underlying concepts and extend their scripts beyond basic conversions.

* **How To Guides**

  The :ref:`How To Guides <how_to>` section contains practical guides for using NeuroConv effectively and solve
  common problems.

* **Developer Guide**

  For developers interested in contributing to NeuroConv, the :ref:`Developer Guide <developer_guide>` provides essential information such as
  instructions for building your own classes,  our coding style, instructions on how to build the documentation,
  run the testing suite, etc.

* **API Reference**

  Detailed documentation of the **nwb2bids** API can be found in the :ref:`API <api>` section.


Do you find that some information is missing or some section lacking or unclear? Reach out with an issue or pull request on our `GitHub repository <https://github.com/catalystneuro/neuroconv>`_.
We are happy to help and appreciate your feedback.



Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   api/index



Related links
-------------

`NWB Overview <https://nwb-overview.readthedocs.io/en/latest/>`_: An overview of the NWB standard and ecosystem

`NWB Guide <https://nwb-guide.readthedocs.io/en/latest/>`_: A no-code solution to conversion to NWB format

`NeuroConv <https://neuroconv.readthedocs.io/en/latest/>`_: A low-code Python library for conversion to NWB format

`NWB Format Specification <https://nwb-schema.readthedocs.io/en/latest/>`_: More information regarding the core NWB
format

`BIDS Specification <https://bids.neuroimaging.io/>`_: More information regarding the core BIDS standard


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
