# Building Documentation Locally

To build the documentation, ensure you have all the necessary plugins installed:

```bash
pip install -e . --group docs
```

then run locally using `Make` (with working directory being the `docs/` directory):

```bash
make html
```

or without `Make`:

```bash
rm -rf _build
sphinx-build -b html -W --keep-going . _build
```

Then view the built documentation by opening `docs/_build/html/index.html` in your favorite web browser.
