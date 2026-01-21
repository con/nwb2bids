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

Documentation Tests
~~~~~~~~~~~~~~~~~~~

Tutorial code blocks are tested using `sybil <https://sybil.readthedocs.io/>`_ to ensure examples stay in sync with the codebase.

Run all doc tests:

.. code-block:: bash

   pytest docs/ -v

For debugging, you must specify each code block you want to run by line number:

.. code-block:: bash

   # List available doc tests with their line numbers
   pytest docs/tutorials.rst --collect-only

   # Run specific code blocks. Always use column:1.
   pytest "docs/tutorials.rst::line:30,column:1" \
          "docs/tutorials.rst::line:158,column:1" \
          "docs/tutorials.rst::line:183,column:1" -v

Hidden assertions use ``.. invisible-code-block: python`` directives which run during testing but don't render in the documentation.

CI Troubleshooting
~~~~~~~~~~~~~~~~~~

For debugging CI failures interactively, use the **Custom dispatch tests** workflow which supports `tmate <https://tmate.io/>`_ debugging sessions.

1. Go to `Custom dispatch tests workflow <https://github.com/con/nwb2bids/actions/workflows/custom_dispatch_tests.yml>`_

2. Click **"Run workflow"**

3. Select the desired OS and Python version from the dropdowns

4. Check **"Enable tmate debugging session"**

5. Click **"Run workflow"** to start

6. Monitor the workflow run. When it reaches the "Setup tmate session" step, it will display an SSH command like::

      ssh randomstring@nyc1.tmate.io

7. Use this command to connect to the CI environment

The session runs under `tmux <https://github.com/tmux/tmux/wiki>`_. Quick reference:

- ``Ctrl-b ?`` - show help with all keybindings
- ``Ctrl-b d`` - detach from session (workflow continues)
- ``Ctrl-b c`` - create new window
- ``Ctrl-b n`` / ``Ctrl-b p`` - next/previous window

When you exit tmux (``exit`` or ``Ctrl-d``), the workflow continues to completion.


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

Container CLI Testing
~~~~~~~~~~~~~~~~~~~~~

CLI tests can be run against a Docker container to verify the packaged application works correctly.

First, build the dev container:

.. code-block:: bash

   docker build -f containers/Dockerfile.dev -t nwb2bids:dev .

Run CLI tests against the container:

.. code-block:: bash

   pytest -m container_cli_test -v --container-image=nwb2bids:dev

This runs all tests marked with ``@pytest.mark.container_cli_test`` inside the specified container.
The test fixture automatically handles volume mounts and environment setup.

Docker
------

TODO

Documentation
-------------

.. include:: README.md
   :parser: myst_parser.sphinx_
