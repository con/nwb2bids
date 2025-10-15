# Documentation

To build the documentation locally:

```bash
# Install documentation dependencies
pip install -e . --group docs

# Clean any previous local runs first
rm -r ./docs/_build

# Build
sphinx-build -b html -W --keep-going docs ./docs/_build

# View the built documentation
# Open ./docs/_build/html/index.html in your favorite web browser
```
