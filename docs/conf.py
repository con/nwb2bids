"""Configuration file for the Sphinx documentation builder."""

import pathlib
import sys

# Add source directory to path for autodoc
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

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
    "sphinx_toggleprompt",  # Used to control >>> behavior in the doctests
    "myst_parser",  # For including Markdown files to be rendered as RST
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

html_static_path = ["_static"]
html_css_files = ["custom.css"]

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

# Toggleprompt
toggleprompt_offset_right = 45  # This controls the position of the prompt (>>>) for the conversion gallery
toggleprompt_default_hidden = "true"

# Copybutton
copybutton_exclude = '.linenos, .gp'  # This avoids copying prompt (>>>) in the conversion gallery (issue #1465)

# MyST
myst_enable_extensions = [
    "colon_fence",      # ::: fences
    "deflist",          # Definition lists
    "fieldlist",        # Field lists
    "html_admonition",  # HTML-style admonitions
    "html_image",       # HTML images
    "replacements",     # Text replacements
    "smartquotes",      # Smart quotes
    "strikethrough",    # ~~strikethrough~~
    "substitution",     # Variable substitutions
    "tasklist",         # Task lists
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
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

rst_epilog = """

.. _BIDS: https://bids.neuroimaging.io/
.. _NWB: https://www.nwb.org/
.. _BIDS Specification: https://bids-specification.readthedocs.io/
"""


def setup(app):
    app.connect("html-page-context", remove_section_nav)

def remove_section_nav(app, pagename, templatename, context, doctree):
    if doctree:
        # Count the number of top-level sections
        sections = [node for node in doctree.traverse() if node.tagname == "section"]
        if len(sections) <= 1:
            # Remove the 'sidebar-secondary' if it exists
            context["sidebars"] = [sidebar for sidebar in context.get("sidebars", []) if sidebar != "sidebar-secondary"]
