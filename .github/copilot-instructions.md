# GitHub Copilot Instructions

## Pull Request Titles

Write PR titles in the past tense (e.g., "Added feature X", "Fixed bug Y", "Updated dependency Z").

## Build and Test

Run tests with:

```bash
pip install -e ".[all]" --quiet && pip install pytest --quiet && pytest tests/ --ignore=tests/unit/test_remote_dataset_converter.py --ignore=tests/integration/test_remote_convert_nwb_dataset.py
```

## Code Style

- Keep code flat and avoid high cyclomatic complexity. Use early exits and guard clauses to reduce nesting. Never exceed 2-3 levels of nesting.
- Never use single-character variable names. Use descriptive names; short forms like `notif` are acceptable, but never a single letter.
- Avoid try/except wherever possible; prefer if/else guard clauses instead. Only use try/except when genuinely unavoidable (e.g., network I/O).

## Docstrings

- CLI `help=` strings must be kept consistent with the corresponding API docstrings (in RunConfig or equivalent). Only add CLI-specific notes when there is a genuine CLI difference.
- First-line docstrings must be no longer than 120 characters in length.

## `__init__.py` Exports

Never expose private functions (prefixed with `_`) in `__init__.py`. Private helpers should only be imported directly from their module.
