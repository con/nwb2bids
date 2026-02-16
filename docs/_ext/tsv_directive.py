"""Custom Sphinx directive for rendering TSV files as HTML tables.

This directive renders TSV files as styled HTML tables while preserving
the ability to copy-paste as tab-separated values.
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective


class TSVTableDirective(SphinxDirective):
    """Directive to render TSV files as HTML tables with proper styling.

    This directive reads a TSV file and renders it as an HTML table with:
    - Proper alignment and styling
    - Ability to copy-paste as TSV
    - Line numbers (optional)

    Usage:
        .. tsv-table:: path/to/file.tsv
           :show-linenums:
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "show-linenums": directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        """Process the TSV file and return the HTML table node."""
        # Get the TSV file path relative to the source directory
        env = self.env
        rel_filename, filename = env.relfn2path(self.arguments[0])

        # Check if file exists
        filepath = Path(filename)
        if not filepath.exists():
            return [self.state_machine.reporter.warning(
                f'TSV file not found: {filename}',
                line=self.lineno
            )]

        # Read the TSV file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [self.state_machine.reporter.warning(
                f'Error reading TSV file {filename}: {e}',
                line=self.lineno
            )]

        # Parse TSV with pandas
        try:
            df = pd.read_csv(
                io.StringIO(content),
                sep="\t",
                dtype=str,
                index_col=False,
                keep_default_na=False,
                header="infer",
            )
        except Exception as e:
            return [self.state_machine.reporter.warning(
                f'Error parsing TSV file {filename}: {e}',
                line=self.lineno
            )]

        # Determine if we should show line numbers
        show_linenums = "show-linenums" in self.options

        # Generate HTML table
        html = self._generate_html_table(df, show_linenums, content)

        # Create raw HTML node
        raw_node = nodes.raw('', html, format='html')
        raw_node['classes'] = ['tsv-table-container']

        return [raw_node]

    def _generate_html_table(self, df: pd.DataFrame, show_linenums: bool, raw_content: str) -> str:
        """Generate HTML table from DataFrame.

        Args:
            df: DataFrame containing TSV data
            show_linenums: Whether to show line numbers
            raw_content: Raw TSV content for copy functionality

        Returns:
            HTML string for the table
        """
        # Build table class
        table_classes = ["tsv-table"]
        if show_linenums:
            table_classes.append("index")
        else:
            table_classes.append("noindex")

        # Build HTML table manually for better control
        html_parts = []
        html_parts.append(f'<table class="{" ".join(table_classes)}">')

        # Header row
        html_parts.append('<thead><tr>')
        if show_linenums:
            html_parts.append('<th></th>')  # Empty cell for line number column
        for col in df.columns:
            html_parts.append(f'<th>{self._escape_html(col)}</th>')
        html_parts.append('</tr></thead>')

        # Body rows
        html_parts.append('<tbody>')
        for line_num, (idx, row) in enumerate(df.iterrows(), start=2):
            html_parts.append('<tr>')
            if show_linenums:
                html_parts.append(f'<td>{line_num}</td>')  # Start at line 2 (line 1 is header)
            for val in row:
                html_parts.append(f'<td>{self._escape_html(val)}</td>')
            html_parts.append('</tr>')
        html_parts.append('</tbody>')

        html_parts.append('</table>')

        # Join without newlines to preserve copy-paste behavior
        return ''.join(html_parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def setup(app):
    """Register the directive with Sphinx."""
    app.add_directive('tsv-table', TSVTableDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
