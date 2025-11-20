:html_theme.sidebar_secondary.remove:

.. _developer_guide:

Developer Guide
===============

Philosophy
----------

TODO

Design
------

TODO

Testing
-------

This project uses ``pytest`` for testing with comprehensive coverage across multiple platforms and Python versions.

Tests are organized into three categories:

- **Unit tests** (``tests/unit/``): Test individual components in isolation
- **Integration tests** (``tests/integration/``): Test interactions between components
- **CLI tests** (``tests/convert_nwb_dataset/``): Test command-line interface behavior

Some tests are marked as ``remote`` when they require downloading data from remote sources (e.g., DANDI Archive).

Running Tests Locally
~~~~~~~~~~~~~~~~~~~~~~

.. note::

   Installing with ``[all]`` extra includes the ``dandi`` optional dependencies needed only for remote tests.

First, install the package with test dependencies:

.. code-block:: bash

   pip install -e ".[all]" --group test

For coverage reporting, also add the ``coverage`` group:

.. code-block:: bash

   pip install -e ".[all]" --group test --group coverage

Run non-remote tests (does not require network):

.. code-block:: bash

   pytest -m "not remote" -vv

Run only remote tests:

.. code-block:: bash

   pytest -m "remote" -vv

Run tests with coverage:

.. code-block:: bash

   pytest -m "not remote" -vv --cov=nwb2bids --cov-report html

The coverage report will be generated in ``htmlcov/index.html``.


Releasing
---------

This repo uses Auto (https://github.com/intuit/auto) with ``hatch-vcs`` to cut releases from PR labels.

The workflow is as follows:

- One-time setup: run the GitHub Action "Setup Release Labels" to create Auto's full default label set in this repo (includes the semver labels and other labels used by Auto and enabled plugins).

- For a release PR: add both of the following labels to the PR before merging:

  - One semver label: ``major``, ``minor``, or ``patch`` (controls version bump).
  - The ``release`` label (authorizes publishing).

- After merge to ``main``, the **"Release with Auto"** workflow will:

  - Compute the next version from labels on merged PRs.
  - Create and push a Git tag (e.g., ``v1.2.3``) and a GitHub Release with a changelog.

- When the GitHub Release is published, the existing **"Upload Package to PyPI"** workflow builds from that tag and uploads to PyPI. The version is derived from the Git tag via ``hatch-vcs``.

.. note::

   Only PRs with the ``release`` label will trigger a release; other PRs are collected until a release-labeled PR is merged.

   You can trigger a release manually via the ``Release with Auto`` workflow dispatch if needed.

   If labels ever get out of sync, re-run the ``Setup Release Labels`` workflow to re-seed the full set.

Docker
------

TODO

Documentation
-------------

.. include:: README.md
   :parser: myst_parser.sphinx_
