This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MANDATORY: Read before making any code changes

You MUST read `docs/developer_guide.rst` before making any code changes, commits, or pull requests.

It contains the authoritative project conventions including:
- Testing categories (unit, integration, CLI) and how to run them
- Assertion style (actual on left, expected on right)
- Releasing workflow (Auto + hatch-vcs, PR labels for semver bumps)
- Changelog conventions (past tense PR titles, label-to-section mapping)
- CI troubleshooting (custom dispatch with tmate)
- Container CLI testing

Do NOT guess or assume conventions -- read the file. Additional documentation may be found under `docs/`.
