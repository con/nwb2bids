"""Configuration file for the Sphinx documentation builder."""

project = "nwb2bids"
copyright = "2025, Cody Baker"
author = "Cody Baker"

extensions = []

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
