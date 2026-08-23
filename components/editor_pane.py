"""Editor Pane Component

QSplitter subclass holding CustomEditor and CustomPreview widgets.
Manages view modes: 'code', 'split', and 'preview'.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter

from components.editor import CustomEditor
from components.preview import CustomPreview


class EditorPane(QSplitter):
    """Splitter container for Markdown Editor and HTML Preview."""

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)

        self.editor = CustomEditor(self)
        self.preview = CustomPreview(self)

        self.addWidget(self.editor)
        self.addWidget(self.preview)

        # Prevent widgets from collapsing completely
        self.setChildrenCollapsible(False)

        # Default mode
        self.set_mode("split")

    def set_mode(self, mode_name: str):
        """Toggle pane visibility according to mode_name.

        Args:
            mode_name (str): One of 'code', 'split', 'preview'.
        """
        mode = mode_name.lower()
        if mode == "code":
            self.editor.show()
            self.preview.hide()
        elif mode == "preview":
            self.editor.hide()
            self.preview.show()
        elif mode == "split":
            self.editor.show()
            self.preview.show()
            # Distribute width equally
            total_width = max(self.width(), 800)
            half = total_width // 2
            self.setSizes([half, half])
