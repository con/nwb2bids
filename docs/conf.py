"""Configuration file for the Sphinx documentation builder."""

import sys
from pathlib import Path

# Add source directory to path for autodoc
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

# Project details
project = "nwb2bids"
copyright = "2025, Cody Baker"
author = "Cody Baker"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
]

# HTML configuration
html_theme = "pydata_sphinx_theme"
html_favicon = "assets/favicon.ico"

html_theme_options = {
    "github_url": "https://github.com/con/nwb2bids",
    "use_edit_page_button": True,
    "show_toc_level": 2,
    "logo": {
        "image_light": "assets/nwb2bids-black.svg",
        "image_dark": "assets/nwb2bids-white.svg",
    }
}

html_context = {
    "github_user": "con",
    "github_repo": "nwb2bids",
    "github_version": "main",
    "doc_path": "docs",
}

# Format signatures for better readability
autodoc_typehints = "signature"
autodoc_typehints_format = "short"
python_maximum_signature_line_length = 88

# Link checker
linkcheck_anchors = False
linkcheck_ignore = []

# Disable sidebars for specific sections
html_sidebars = {
    'user_guide': [],
    'tutorials': [],
    "developer_guide": [],
}

# --------------------------------------------------
# Extension configuration
# --------------------------------------------------

# Napoleon
napoleon_google_docstring = False          # Disable support for Google-style docstrings (use NumPy-style instead)
napoleon_numpy_docstring = True            # Enable support for NumPy-style docstrings
napoleon_use_param = False                 # Do not convert :param: sections into Parameters; leave as-is
napoleon_use_ivar = True                   # Interpret instance variables as documented with :ivar:

# Autodoc
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "private-members": False,
    "undoc-members": True,
    "show-inheritance": False,
    "exclude-members": "__new__,model_dump",
}
add_module_names = False
toc_object_entries_show_parents = "hide"

def setup(app):
    app.connect("html-page-context", remove_section_nav)

def remove_section_nav(app, pagename, templatename, context, doctree):
    if doctree:
        # Count the number of top-level sections
        sections = [node for node in doctree.traverse() if node.tagname == "section"]
        if len(sections) <= 1:
            # Remove the 'sidebar-secondary' if it exists
            context["sidebars"] = [sidebar for sidebar in context.get("sidebars", []) if sidebar != "sidebar-secondary"]
