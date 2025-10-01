"""Configuration file for the Sphinx documentation builder."""

import sys
from pathlib import Path

# Add source directory to path for autodoc
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

project = "nwb2bids"
copyright = "2025, Cody Baker"
author = "Cody Baker"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

exclude_patterns = []

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/con/nwb2bids",
    "use_edit_page_button": True,
    "show_toc_level": 2,
}

html_context = {
    "github_user": "con",
    "github_repo": "nwb2bids",
    "github_version": "main",
    "doc_path": "docs/source",
}

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_ivar = True

# Autodoc settings
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "private-members": False,
    "undoc-members": True,
    "show-inheritance": False,
    "exclude-members": "__new__",
}
add_module_names = False
toc_object_entries_show_parents = "hide"

# Format signatures for better readability
autodoc_typehints = "signature"
autodoc_typehints_format = "short"
python_maximum_signature_line_length = 88
