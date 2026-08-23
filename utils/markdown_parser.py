"""Markdown Parser Utility

Converts raw Markdown text into rendered HTML string using python-markdown extensions.
"""

import markdown


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
    return markdown.markdown(text, extensions=extensions)
