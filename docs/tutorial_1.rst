.. _tutorial-single-file-test:

Tutorial 1 - Converting a single file (POC)
-------------------------------------------

This demonstrates doc testing with sybil: bash blocks, python blocks, and hidden assertions.

First, generate the example file:

.. code-block:: bash

    nwb2bids tutorial ephys file

Convert using CLI
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    cd ~/nwb2bids_tutorials/ephys_tutorial_file

    nwb2bids convert ephys.nwb --bids-directory bids_dataset_cli

.. invisible-code-block: python

    bids_dir = Path.home() / "nwb2bids_tutorials/ephys_tutorial_file/bids_dataset_cli"
    assert bids_dir.exists(), "BIDS directory was not created"
    assert (bids_dir / "dataset_description.json").exists()
    assert (bids_dir / "sub-001" / "ses-A" / "ecephys").is_dir()

Convert using Python
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pathlib
    import nwb2bids

    tutorial_directory = pathlib.Path.home() / "nwb2bids_tutorials/ephys_tutorial_file"
    nwb_paths = [tutorial_directory / "ephys.nwb"]
    bids_directory = tutorial_directory / "bids_dataset_py"
    bids_directory.mkdir(exist_ok=True)

    run_config = nwb2bids.RunConfig(bids_directory=bids_directory)
    converter = nwb2bids.convert_nwb_dataset(
        nwb_paths=nwb_paths,
        run_config=run_config,
    )

.. invisible-code-block: python

    bids_dir = pathlib.Path.home() / "nwb2bids_tutorials/ephys_tutorial_file/bids_dataset_py"
    assert bids_dir.exists(), "BIDS directory was not created"
    assert (bids_dir / "dataset_description.json").exists()
    assert (bids_dir / "sub-001" / "ses-A" / "ecephys").is_dir()
