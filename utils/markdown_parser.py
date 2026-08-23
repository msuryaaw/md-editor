"""Markdown Parser Utility

Converts raw Markdown text into rendered HTML string using python-markdown extensions
and Pygments dark syntax highlighting.
"""

import markdown
from pygments.formatters import HtmlFormatter


def get_pygments_dark_css() -> str:
    """Generate Pygments CSS rules for dark syntax highlighting without clashing background properties."""
    formatter = HtmlFormatter(style="monokai", cssclass="codehilite")
    raw_css = formatter.get_style_defs()
    lines = []
    for line in raw_css.splitlines():
        # Remove background properties on token definitions to avoid black redacted blocks in Qt CSS 2.1 engine
        if "background" in line and ".codehilite" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def parse_markdown(text: str) -> str:
    """Convert raw Markdown string to HTML.

    Args:
        text (str): Raw Markdown content.

    Returns:
        str: Rendered HTML content.
    """
    if not text:
        return ""

    extensions = ["fenced_code", "tables", "codehilite", "toc"]
    extension_configs = {
        "codehilite": {
            "css_class": "codehilite",
            "guess_lang": False,
            "use_pygments": True,
        }
    }
    return markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
