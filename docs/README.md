# Documentation

To build the documentation locally:

```bash
# Install documentation dependencies
pip install -e . --group docs
cd docs

# Unix: Build HTML documentation
make html

# Windows: Build HTML documentation
sphinx-build -b html docs ./docs/_build/html

# View the built documentation
# Open docs/build/html/index.html in your favorite web browser
```
