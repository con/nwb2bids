
.. _developer_guide:

Developer Guide
===============

Design
------

For **basic users**, ``nwb2bids`` is intended to be a simple-to-use tool for converting NWB datasets to BIDS format
with minimal user configuration.

For **advanced users**, ``nwb2bids`` is designed to be easily extensible to support new NWB data types, BIDS extensions,
and custom configurable behavior.

Whenever working on a new feature, keep in mind how to make it easy to understand and use for the **basic users**,
while still being flexible enough for the **advanced users**.



Philosophy
----------

``nwb2bids`` is also designed with the following principles in mind:

- **Modularity**: The codebase is organized into clear, modular components that encapsulate specific functionality. This makes it easier to maintain, test, and extend the code.

- **Extensibility**: The architecture allows for easy addition of new features, data types, and configurations without requiring major changes to the existing codebase.

- **Readability**: Code should be clean, well-documented, and follow consistent style guidelines to ensure that it is easy to understand and collaborate on.

- **Performance**: While prioritizing usability and extensibility, the code should also be efficient and performant, especially when handling large datasets.

- **Collect and report all notifications**: During conversion, all encountered issues (including internal runtime errors) should be collected and reported to the user at the end, rather than stopping at the first error. This provides a comprehensive overview of any problems that need to be addressed.



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

Building Docs Locally
~~~~~~~~~~~~~~~~~~~~~

.. include:: README.md
   :parser: myst_parser.sphinx_
   :start-line: 2

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

   If labels ever get out of sync, restore and rerun the ``Setup Release Labels`` workflow to re-seed the full set.

Changelog
~~~~~~~~~

The `CHANGELOG.md <https://github.com/con/nwb2bids/blob/main/CHANGELOG.md>`_ file is auto-generated from merged PRs via
the same Auto release process described above.

Each entry is created from the PR title and categorized by the labels applied to the PR.

Custom entries can be created by using the PR description with the following body:

.. code-block:: markdown

   # What Changed

   ### Release Notes

    [ Enter your custom changelog entry here. ]

Refer to `PR #244 <https://github.com/con/nwb2bids/pull/244>`_ and corresponding `v0.9.0 Release Notes <https://github.com/con/nwb2bids/releases/tag/v0.9.0>`_ for an example of this behavior.

**For stylistic consistency**, please name all PR titles using the past tense (e.g., "Fix bug about..." -> "Fixed bug
about...") since these titles become changelog entries.

The label interactions leading to changelog sections are roughly as follows:

- ``minor`` / ``enhancement`` -> 'Feature'
- ``patch`` / ``bug`` -> 'Bug Fix'
- ``documentation`` -> 'Documentation'
- ``internal`` -> 'Internal' (ONLY if no other above labels are present; e.g., `PR #242 <https://github.com/con/nwb2bids/blob/main/CHANGELOG.md>`_ had both ``internal`` and ``patch``, so it appears under 'Bug Fix' instead of 'Internal')
