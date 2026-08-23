"""Toolbar Component

QToolBar subclass providing action buttons for file operation and view mode switcher.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QToolBar


class MainToolBar(QToolBar):
    """Application main toolbar."""

    new_file_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()
    save_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self._setup_actions()

    def _setup_actions(self):
        """Create and layout toolbar actions."""
        # File management actions
        self.new_action = QAction("📄 New File", self)
        self.new_action.setToolTip("Buat file Markdown baru (Ctrl+N)")
        self.new_action.triggered.connect(self.new_file_requested.emit)
        self.addAction(self.new_action)

        self.open_action = QAction("📂 Open Folder", self)
        self.open_action.setToolTip("Buka folder workspace")
        self.open_action.triggered.connect(self.open_folder_requested.emit)
        self.addAction(self.open_action)

        self.save_action = QAction("💾 Save", self)
        self.save_action.setToolTip("Simpan file (Ctrl+S)")
        self.save_action.triggered.connect(self.save_requested.emit)
        self.addAction(self.save_action)

        self.addSeparator()

        # View mode toggle group
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)

        self.code_action = QAction("💻 Code", self)
        self.code_action.setCheckable(True)
        self.code_action.setToolTip("Tampilkan editor saja (100%)")
        self.code_action.triggered.connect(lambda: self.mode_changed.emit("code"))
        mode_group.addAction(self.code_action)
        self.addAction(self.code_action)

        self.split_action = QAction("⚖️ Split", self)
        self.split_action.setCheckable(True)
        self.split_action.setChecked(True)
        self.split_action.setToolTip("Tampilkan editor dan preview (50% / 50%)")
        self.split_action.triggered.connect(lambda: self.mode_changed.emit("split"))
        mode_group.addAction(self.split_action)
        self.addAction(self.split_action)

        self.preview_action = QAction("👁️ Preview", self)
        self.preview_action.setCheckable(True)
        self.preview_action.setToolTip("Tampilkan preview HTML saja (100%)")
        self.preview_action.triggered.connect(lambda: self.mode_changed.emit("preview"))
        mode_group.addAction(self.preview_action)
        self.addAction(self.preview_action)

    def set_active_mode(self, mode_name: str):
        """Update checked state of view mode toolbar buttons.

        Args:
            mode_name (str): Identifier ('code', 'split', 'preview').
        """
        mode = mode_name.lower()
        if mode == "code":
            self.code_action.setChecked(True)
        elif mode == "preview":
            self.preview_action.setChecked(True)
        else:
            self.split_action.setChecked(True)
