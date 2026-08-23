"""Custom Editor Component

QTextEdit subclass emitting custom content_changed signal.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QTextEdit


class CustomEditor(QTextEdit):
    """Custom Markdown text editor widget."""

    content_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ketik Markdown di sini...")
        self._setup_style()
        self.textChanged.connect(self._on_text_changed)

    def _setup_style(self):
        """Configure monospaced font and tab spacing."""
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Tab stop distance to 4 space characters
        metrics = QFontMetrics(font)
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))

    def _on_text_changed(self):
        """Emit content_changed signal with updated plaintext content."""
        self.content_changed.emit(self.toPlainText())
