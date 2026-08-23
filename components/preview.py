"""Custom Preview Component

QTextBrowser subclass for displaying rendered Markdown HTML.
"""

from PyQt6.QtWidgets import QTextBrowser


class CustomPreview(QTextBrowser):
    """Custom preview widget for HTML output."""

    DEFAULT_STYLE = """
    <style>
        body {
            font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #24292e;
            padding: 16px;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 20px;
            margin-bottom: 12px;
            font-weight: 600;
            color: #1f2328;
        }
        h1 { font-size: 2em; border-bottom: 1px solid #d8dee4; padding-bottom: 0.3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #d8dee4; padding-bottom: 0.3em; }
        h3 { font-size: 1.25em; }
        code {
            font-family: Consolas, "Courier New", monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-size: 85%;
        }
        pre {
            background-color: #f6f8fa;
            padding: 14px;
            border-radius: 6px;
            font-family: Consolas, "Courier New", monospace;
            font-size: 85%;
            line-height: 1.45;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            margin: 0;
            padding: 0 1em;
            color: #57606a;
            border-left: 0.25em solid #d0d7de;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        table th, table td {
            padding: 6px 13px;
            border: 1px solid #d0d7de;
        }
        table th {
            font-weight: 600;
            background-color: #f6f8fa;
        }
        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        ul, ol {
            padding-left: 2em;
        }
    </style>
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)

    def render_html(self, html_str: str):
        """Render HTML content with embedded custom stylesheet.

        Args:
            html_str (str): Raw HTML string to display.
        """
        styled_html = f"<html><head>{self.DEFAULT_STYLE}</head><body>{html_str}</body></html>"
        self.setHtml(styled_html)
