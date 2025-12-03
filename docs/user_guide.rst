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



Application Programming Interface (API)
---------------------------------------

A more advanced usage of **nwb2bids** is through its Python library. A thorough description of all publicly exposed
functions and classes can be found in the :ref:`API <api>` section of the documentation.

The core function is the ``convert_nwb_to_bids`` function, which can be used as follows:

.. code-block:: python

   import nwb2bids

   nwb2bids.convert_nwb_to_bids(
       nwb_paths=["path/to/many/nwb", "single.nwb", "another.nwb"],
       bids_directory="path/to/bids/directory"  # Optional, defaults to current working directory
   )

Essentially, this function is direct wrapper used by the CLI and behaves in the same way.

One key programmatic difference however is the ability to interact with the notifications returned by the operation:

.. code-block:: python

   import nwb2bids

   notifications = nwb2bids.convert_nwb_to_bids(
       nwb_paths=["path/to/many/nwb", "single.nwb", "another.nwb"],
       bids_directory="path/to/bids/directory"
   )

   for notification in notifications:
       print(notification)



Using Containers
----------------

You can run **nwb2bids** without installing it locally using Docker, Podman, Apptainer, or Singularity.

.. tabs::

   .. tab:: Docker

      .. code-block:: bash

         docker run --rm --user $(id -u):$(id -g) -v $(pwd):$(pwd) -v ~/.cache:/.cache -w $(pwd) ghcr.io/con/nwb2bids:latest nwb2bids convert ./my_file.nwb --bids-directory bids_output

   .. tab:: Podman

      .. code-block:: bash

         podman run --rm --userns=keep-id -v $(pwd):$(pwd):Z -w $(pwd) ghcr.io/con/nwb2bids:latest nwb2bids convert ./my_file.nwb --bids-directory bids_output

   .. tab:: Apptainer

      .. code-block:: bash

         apptainer run docker://ghcr.io/con/nwb2bids:latest nwb2bids convert ./my_file.nwb --bids-directory bids_output

   .. tab:: Singularity

      .. code-block:: bash

         singularity run docker://ghcr.io/con/nwb2bids:latest nwb2bids convert ./my_file.nwb --bids-directory bids_output
