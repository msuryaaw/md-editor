"""Custom Preview Component

QTextBrowser subclass for displaying rendered Markdown HTML styled with GitHub Dark Theme (CSS 2.1 compatible).
Supports remote image fetching (HTTP/HTTPS badges) via loadResource override.
"""

import urllib.request
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QTextBrowser

from utils.markdown_parser import get_pygments_dark_css


class CustomPreview(QTextBrowser):
    """Custom HTML preview widget for rendered Markdown in GitHub Dark style."""

    GITHUB_DARK_CSS = """
    <style>
        /* Body & Layout */
        body {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            padding: 16px;
            margin: 0;
        }

        /* Headings dengan Border Bawah Presisi GitHub */
        h1, h2 {
            color: #f0f6fc;
            font-weight: 600;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #21262d;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; color: #f0f6fc; margin-top: 20px; }
        h4 { font-size: 1em; color: #f0f6fc; }

        /* FIX CRITICAL: Eliminasi Belang/Garis Hitam di Code Block */
        pre {
            background-color: #161b22 !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            padding: 14px !important;
            border-radius: 6px !important;
            font-family: 'Consolas', 'Courier New', monospace !important;
            font-size: 13px !important;
            line-height: 1.45 !important;
            white-space: pre !important;
            margin-bottom: 16px !important;
        }

        /* Paksa seluruh anak elemen di dalam pre agar background-nya transparan total */
        pre *, pre span, pre code {
            background-color: transparent !important;
            background: none !important;
            font-family: 'Consolas', 'Courier New', monospace !important;
        }

        code {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 2px 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 85%;
        }

        /* Tables Styling Presisi */
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 12px;
            margin-bottom: 16px;
            border: 1px solid #30363d;
        }
        th, td {
            padding: 8px 13px;
            border: 1px solid #30363d;
        }
        th {
            background-color: #161b22;
            color: #f0f6fc;
            font-weight: 600;
            text-align: left;
        }
        tr:nth-child(even) { background-color: #161b22; }
        tr:nth-child(odd) { background-color: #0d1117; }

        /* Lists & Tasklists */
        ul, ol {
            padding-left: 2em;
            margin-top: 0;
            margin-bottom: 16px;
        }
        li {
            margin-top: 0.25em;
        }
        blockquote {
            padding: 0 1em;
            color: #8b949e;
            border-left: 0.25em solid #30363d;
            margin: 0 0 16px 0;
        }
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #30363d;
            border: 0;
        }
        a {
            color: #58a6ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        img {
            max-width: 100%;
            vertical-align: middle;
            background-color: transparent;
        }

        /* GitHub Dark Token Colors for Code Block */
        .highlight .k, .highlight .kd, .highlight .kn, .codehilite .k, .codehilite .kd, .codehilite .kn { color: #ff7b72; font-weight: bold; }
        .highlight .s, .highlight .s2, .highlight .se, .codehilite .s, .codehilite .s2, .codehilite .se { color: #a5d6ff; }
        .highlight .nf, .highlight .fm, .codehilite .nf, .codehilite .fm { color: #d2a8ff; }
        .highlight .c, .highlight .c1, .codehilite .c, .codehilite .c1 { color: #8b949e; font-style: italic; }
        .highlight .nb, .highlight .nc, .codehilite .nb, .codehilite .nc { color: #ffa657; }
        .highlight .mi, .highlight .mf, .codehilite .mi, .codehilite .mf { color: #79c0ff; }
        .highlight .o, .highlight .p, .codehilite .o, .codehilite .p { color: #f0f6fc; }

        /* Pygments Dark Syntax Highlighting Fallback */
        {pygments_css}
    </style>
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self._image_cache = {}

    def loadResource(self, type_id, name: QUrl):
        """Fetch and cache remote image resources (HTTP/HTTPS) for QTextBrowser."""
        if type_id == QTextDocument.ResourceType.ImageResource and name.scheme() in ["http", "https"]:
            url_str = name.toString()

            # Check cache
            if url_str in self._image_cache:
                return self._image_cache[url_str]

            try:
                req = urllib.request.Request(
                    url_str,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                )
                with urllib.request.urlopen(req, timeout=3) as response:
                    image_data = response.read()
                    self._image_cache[url_str] = image_data
                    return image_data
            except Exception as e:
                # Log error silently and delegate to parent
                pass

        return super().loadResource(type_id, name)

    def render_html(self, html_str: str):
        """Render HTML string wrapped in GitHub Dark Theme CSS.

        Args:
            html_str (str): Raw HTML content to display.
        """
        pygments_css = get_pygments_dark_css()
        full_css = self.GITHUB_DARK_CSS.replace("{pygments_css}", pygments_css)
        styled_html = f"<html><head>{full_css}</head><body>{html_str}</body></html>"
        self.setHtml(styled_html)
