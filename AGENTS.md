# Agent instructions

## Commits and PRs

- Always run `pre-commit` before committing and pushing changes
- Always link PRs to issues when possible
- PR titles should be human-readable and in the past tense. They should NOT use conventional commit style.
- Every commit must include a `Co-Authored-By` trailer identifying your tool name and version and your underlying model and version. Format (replace all `<…>` placeholders with actual values): `Co-Authored-By: <Tool> <tool-version> / <Model> <model-version> <noreply@vendor-domain>`

## Code style

- Require keyword-only arguments `(*, ...)` for multi-input functions. For any function with exactly one caller-supplied parameter (excluding `self` and `cls`), require positional-only usage with the `/` designator.
- Always add new imports at the top of the file. The only exception is when a local import is needed to avoid a circular dependency.
- For external dependencies, use the full module import style (e.g., `import xyz; xyz.abc`) rather than `from xyz import abc`.
- For internal imports, always use relative style (e.g., `from .foo import bar`).
- Prefer assigning return values to named locals before `return` when this improves readability and debugger breakpoint placement.
- Avoid excessive em-dashes, colons, and semicolons in written text such as documentation. Prefer breaking into separate, shorter sentences instead.
- Favor defining one-word names for CLI flags, then map those onto longer, more explicit keyword arguments at the API level.

## Tests

- To the best of your ability, ensure tests are passing before pushing.
- Follow assertion style: actual on left, expected on right.
- Always mark AI-generated tests with the `ai_generated` pytest marker.
- Use `pytest.mark.parametrize` wherever appropriate to reduce duplication in test cases.
- Avoid importing private API (names with a leading underscore) in tests. Always import from what is publicly exposed through `__init__.py` files.
- When monkeypatching internal imports in tests, target the importing module's binding (e.g., `foo.baz`), not the original definition module (e.g., `foo._bar.baz`).

## Module and API conventions

- Never expose private names (those with a leading underscore) in any module's `__all__`.
- Never include code other than imports, `__all__`, simple import errors, or magic `__dir__` overrides in any `__init__.py` file.
- Do not add compatibility aliases when renaming functions. Update all call sites to the canonical name instead.
