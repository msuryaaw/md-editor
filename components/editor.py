"""Custom Editor Component

QTextEdit subclass emitting custom content_changed signal,
with MarkdownHighlighter for raw Markdown code coloring in GitHub Dark palette.
"""

from PyQt6.QtCore import QRegularExpression, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtWidgets import QTextEdit


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for raw Markdown text using GitHub Dark color palette."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []
        self._setup_rules()

    def _setup_rules(self):
        # 1. Headers (#, ##, etc) -> #d2a8ff (Light Purple, Bold)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#d2a8ff"))
        header_format.setFontWeight(QFont.Weight.Bold)
        self._rules.append((QRegularExpression(r"^#{1,6}\s+.*$"), header_format))

        # 2. Bold (**text** or __text__) -> #ffa657 (Orange, Bold)
        bold_format = QTextCharFormat()
        bold_format.setForeground(QColor("#ffa657"))
        bold_format.setFontWeight(QFont.Weight.Bold)
        self._rules.append((QRegularExpression(r"\*\*.*?\*\*|__.*?__"), bold_format))

        # 3. Italic (*text* or _text_) -> #e3b341 (Yellow, Italic)
        italic_format = QTextCharFormat()
        italic_format.setForeground(QColor("#e3b341"))
        italic_format.setFontItalic(True)
        self._rules.append(
            (
                QRegularExpression(r"(?<!\*)\*[^\*]+?\*(?!\*)|(?<!_)_[^_]+?_(?!_)"),
                italic_format,
            )
        )

        # 4. Inline Code (`code`) & Code blocks (```) -> #7ee787 (Bright Green)
        code_format = QTextCharFormat()
        code_format.setForeground(QColor("#7ee787"))
        self._rules.append((QRegularExpression(r"`[^`]+`"), code_format))
        self._rules.append((QRegularExpression(r"^```.*$"), code_format))

        # 5. Links ([text](url)) -> #58a6ff (Bright Blue)
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#58a6ff"))
        self._rules.append((QRegularExpression(r"\[.*?\]\(.*?\)|https?://\S+"), link_format))

        # 6. Blockquotes (>) -> #8b949e (Grey)
        quote_format = QTextCharFormat()
        quote_format.setForeground(QColor("#8b949e"))
        self._rules.append((QRegularExpression(r"^>\s+.*$"), quote_format))

        # 7. Lists (- *, 1.) -> #8b949e (Grey)
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#8b949e"))
        self._rules.append((QRegularExpression(r"^\s*([*\-+]|\d+\.)\s+"), list_format))

    def highlightBlock(self, text: str):
        """Apply syntax highlighting rules to text block."""
        for expression, format_style in self._rules:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_style)


class CustomEditor(QTextEdit):
    """Custom Markdown text editor widget."""

    content_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ketik Markdown di sini...")
        self._setup_style()
        self.highlighter = MarkdownHighlighter(self.document())
        self.textChanged.connect(self._on_text_changed)

    def _setup_style(self):
        """Configure monospaced font and tab spacing."""
        font = QFont("Consolas", 11)
        font.setFamilies(["Cascadia Code", "Fira Code", "Consolas", "Courier New", "monospace"])
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Tab stop distance to 4 space characters
        metrics = QFontMetrics(font)
        self.setTabStopDistance(4 * metrics.horizontalAdvance(" "))

    def _on_text_changed(self):
        """Emit content_changed signal with updated plaintext content."""
        self.content_changed.emit(self.toPlainText())
