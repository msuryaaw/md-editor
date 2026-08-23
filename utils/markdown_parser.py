"""Markdown Parser Utility

Converts raw Markdown text into rendered HTML string using python-markdown extensions,
tasklist checkbox replacement, and Pygments dark syntax highlighting.
"""

import re
import markdown
from pygments.formatters import HtmlFormatter


def get_pygments_dark_css() -> str:
    """Generate Pygments CSS rules for dark syntax highlighting without any background properties."""
    formatter = HtmlFormatter(style="monokai", cssclass="highlight")
    raw_css = formatter.get_style_defs()
    lines = []
    for line in raw_css.splitlines():
        # Remove all background properties to ensure transparent background inside <pre> blocks in Qt QTextBrowser
        if "background" in line:
            continue
        lines.append(line)
    return "\n".join(lines)


def _convert_tasklists(text: str) -> str:
    """Replace Markdown tasklist syntax ([x] and [ ]) with Unicode checkbox glyphs.

    Args:
        text (str): Raw Markdown content.

    Returns:
        str: Transformed Markdown string with Unicode checkboxes.
    """
    # Replace checked tasklist item: '- [x]' or '* [x]' -> '- ☑ '
    text = re.sub(r"(\s*[\*\-\+]\s+)\[[xX]\]", r"\1☑ ", text)
    # Replace unchecked tasklist item: '- [ ]' or '* [ ]' -> '- ☐ '
    text = re.sub(r"(\s*[\*\-\+]\s+)\[\s\]", r"\1☐ ", text)
    return text


def parse_markdown(text: str) -> str:
    """Convert raw Markdown string to HTML.

    Args:
        text (str): Raw Markdown content.

    Returns:
        str: Rendered HTML content.
    """
    if not text:
        return ""

    # Pre-process tasklist checkboxes
    processed_text = _convert_tasklists(text)

    # Pre-process: Ensure blank line before list items (* - + 1.) if preceded by plain text line
    processed_text = re.sub(r"([^\n])\n([ \t]*[*+\-]|\d+\.) ", r"\1\n\n\2 ", processed_text)

    extensions = ["fenced_code", "tables", "codehilite", "toc", "sane_lists"]
    extension_configs = {
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
            "use_pygments": True,
        }
    }
    return markdown.markdown(
        processed_text, extensions=extensions, extension_configs=extension_configs
    )
