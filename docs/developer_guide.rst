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

TODO

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

TODO
