:html_theme.sidebar_secondary.remove:

.. _user_guide:

User Guide
==========

Command Line Interface (CLI)
----------------------------

The easiest way to use **nwb2bids** is through the terminal invocation:

.. code-block:: bash

   nwb2bids convert [path to NWB files]

This command assumes you are located within either an empty directory or a BIDS dataset, informing you accordingly if
these conditions are not met.

To specify a specific location other than your current working directory, use the ``--bids-directory``
flag (or ``-o`` for short):

.. code-block:: bash

   nwb2bids convert [path to NWB files] --bids-directory [path to BIDS directory]

The main input to the interface can be any combination of directories containing NWB files or individual NWB files:

.. code-block:: bash

   nwb2bids convert path/to/many/nwb single.nwb another.nwb
