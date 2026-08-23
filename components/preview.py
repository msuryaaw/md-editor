"""Custom Preview Component

QTextBrowser subclass for displaying rendered Markdown HTML styled with GitHub Dark Theme (CSS 2.1 compatible).
"""

from PyQt6.QtWidgets import QTextBrowser

from utils.markdown_parser import get_pygments_dark_css


class CustomPreview(QTextBrowser):
    """Custom HTML preview widget for rendered Markdown in GitHub Dark style."""

    GITHUB_DARK_CSS = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #c9d1d9;
            background-color: #0d1117;
            padding: 24px;
            margin: 0;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: #f0f6fc;
        }
        h1 {
            font-size: 2em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #21262d;
        }
        h2 {
            font-size: 1.5em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #21262d;
        }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: 0.875em; }
        h6 { font-size: 0.85em; color: #8b949e; }

        p {
            margin-top: 0;
            margin-bottom: 16px;
        }

        code {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            color: #e6edf3;
            background-color: #161b22;
        }

        pre {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 10px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            white-space: pre;
            margin-top: 0;
            margin-bottom: 16px;
        }

        pre code {
            background-color: #161b22;
            color: #c9d1d9;
            padding: 0;
            border: none;
            font-size: 100%;
        }

        pre span {
            background-color: #161b22;
        }

        blockquote {
            margin: 0 0 16px 0;
            padding: 0 1em;
            color: #8b949e;
            border-left: 3px solid #30363d;
        }

        table {
            border-spacing: 0;
            border-collapse: collapse;
            margin-top: 0;
            margin-bottom: 16px;
            width: 100%;
        }

        table th, table td {
            padding: 6px 13px;
            border: 1px solid #30363d;
        }

        table th {
            font-weight: 600;
            background-color: #161b22;
            color: #f0f6fc;
        }

        table tr:nth-child(2n) {
            background-color: #161b22;
        }

        table tr:nth-child(2n+1) {
            background-color: #0d1117;
        }

        hr {
            height: 2px;
            padding: 0;
            margin: 24px 0;
            background-color: #30363d;
            border: 0;
        }

        ul, ol {
            margin-top: 0;
            margin-bottom: 16px;
            padding-left: 2em;
        }

        li + li {
            margin-top: 0.25em;
        }

        a {
            color: #58a6ff;
            text-decoration: none;
        }

        /* Pygments Dark Syntax Highlighting */
        {pygments_css}
    </style>
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)

    def render_html(self, html_str: str):
        """Render HTML string wrapped in GitHub Dark Theme CSS.

        Args:
            html_str (str): Raw HTML content to display.
        """
        pygments_css = get_pygments_dark_css()
        full_css = self.GITHUB_DARK_CSS.replace("{pygments_css}", pygments_css)
        styled_html = f"<html><head>{full_css}</head><body>{html_str}</body></html>"
        self.setHtml(styled_html)
