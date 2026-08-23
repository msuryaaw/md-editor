"""Custom Preview Component

QTextBrowser subclass for displaying rendered Markdown HTML styled with GitHub Dark Theme (CSS 2.1 compatible).
Supports remote image fetching (HTTP/HTTPS badges) via loadResource override.
"""

import os
import urllib.request
from urllib.parse import unquote
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice, QUrl
from PyQt6.QtGui import QDesktopServices, QImage, QPainter, QTextDocument
from PyQt6.QtSvg import QSvgRenderer
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
            display: block !important;
            padding-left: 2em !important;
            margin-top: 8px !important;
            margin-bottom: 16px !important;
        }
        li {
            display: list-item !important;
            margin-top: 4px !important;
            margin-bottom: 4px !important;
            color: #c9d1d9 !important;
        }
        /* Tasklist Checkbox Reset */
        li input[type="checkbox"], li span.checkbox {
            margin-right: 6px;
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
        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self._on_anchor_clicked)
        self._image_cache = {}
        self.base_dir = os.getcwd()
        self.strict_mode = True

    def _on_anchor_clicked(self, url: QUrl):
        """Handle clicked hyperlinks: scroll to internal anchors or open external URLs in browser.

        Args:
            url (QUrl): Clicked target URL.
        """
        fragment = url.fragment()
        url_str = url.toString()

        # 1. Handle Internal Anchor Links (#...)
        if fragment or url_str.startswith("#"):
            raw_target = fragment if fragment else url_str.lstrip("#")
            anchor_target = unquote(raw_target)

            # First attempt: scroll to exact anchor target
            self.scrollToAnchor(anchor_target)

            # Second attempt: Fallback for GitHub-style emoji slugs (e.g. #-overview -> overview)
            if anchor_target.startswith("-"):
                clean_target = anchor_target.lstrip("-")
                if clean_target:
                    self.scrollToAnchor(clean_target)
        # 2. Handle External HTTP/HTTPS Links
        elif url.scheme() in ["http", "https"]:
            QDesktopServices.openUrl(url)
        # 3. Handle Other Links (e.g. file://)
        else:
            QDesktopServices.openUrl(url)

    def set_base_dir(self, directory: str):
        """Set base directory for resolving local relative image paths."""
        if directory and os.path.exists(directory):
            self.base_dir = directory

    def set_strict_mode(self, enabled: bool):
        """Enable or disable strict security mode for image loading.

        Args:
            enabled (bool): True to block HTTP/HTTPS remote images, False to allow.
        """
        self.strict_mode = enabled
        self._image_cache.clear()

    def _render_svg_to_qimage(self, svg_data: bytes) -> QImage:
        """Render raw SVG bytes into QImage with transparent background."""
        renderer = QSvgRenderer(QByteArray(svg_data))
        if not renderer.isValid():
            img = QImage()
            img.loadFromData(svg_data)
            return img

        size = renderer.defaultSize()
        if size.isEmpty() or size.width() <= 0 or size.height() <= 0:
            size.setWidth(100)
            size.setHeight(20)

        image = QImage(size, QImage.Format.Format_ARGB32)
        image.fill(0)  # Transparent background

        painter = QPainter(image)
        renderer.render(painter)
        painter.end()

        return image

    def loadResource(self, type_id, name: QUrl):
        """Fetch and cache remote image resources (HTTP/HTTPS) and local relative images."""
        if type_id == QTextDocument.ResourceType.ImageResource:
            # Use toEncoded() to preserve percent-encoding (e.g. %20) for urllib requests
            if name.scheme() in ["http", "https"]:
                url_str = bytes(name.toEncoded()).decode("utf-8")
            else:
                url_str = name.toString()

            # 1. Handle HTTP/HTTPS remote images
            if name.scheme() in ["http", "https"]:
                # BLOCK remote images in Strict Security Mode
                if self.strict_mode:
                    return QImage()

                if url_str in self._image_cache:
                    return self._image_cache[url_str]

                try:
                    req = urllib.request.Request(
                        url_str,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                    )
                    with urllib.request.urlopen(req, timeout=3) as response:
                        image_data = response.read()
                        is_svg = url_str.lower().endswith(".svg") or "shields.io" in url_str.lower() or b"<svg" in image_data[:100].lower()
                        if is_svg:
                            qimg = self._render_svg_to_qimage(image_data)
                        else:
                            qimg = QImage()
                            qimg.loadFromData(image_data)

                        if not qimg.isNull():
                            self._image_cache[url_str] = qimg
                            return qimg
                except Exception:
                    pass

            # 2. Handle Local Images (File URL or Relative Paths)
            path_str = name.toLocalFile() if name.scheme() == "file" else url_str
            if path_str:
                # Resolve relative paths against base_dir or cwd
                if not os.path.isabs(path_str):
                    abs_path = os.path.abspath(os.path.join(self.base_dir, path_str))
                else:
                    abs_path = path_str

                if os.path.exists(abs_path):
                    try:
                        with open(abs_path, "rb") as f:
                            image_data = f.read()
                            if abs_path.lower().endswith(".svg") or b"<svg" in image_data[:100].lower():
                                qimg = self._render_svg_to_qimage(image_data)
                            else:
                                qimg = QImage()
                                qimg.loadFromData(image_data)
                            if not qimg.isNull():
                                return qimg
                    except Exception:
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
