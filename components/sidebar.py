"""Sidebar Component

QTreeView subclass wrapped with QFileSystemModel for browsing Markdown workspace files.
"""

from PyQt6.QtCore import QDir, QFileInfo, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QHeaderView, QTreeView


class SidebarTree(QTreeView):
    """File explorer sidebar filtered for Markdown files."""

    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = QFileSystemModel(self)
        self.model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )
        self.model.setNameFilters(["*.md", "*.markdown"])
        self.model.setNameFilterDisables(False)

        # Set model to system root initially
        self.model.setRootPath("")
        self.setModel(self.model)

        # Configure columns: Show only filename column (Column 0)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setColumnHidden(1, True)  # Size
        self.setColumnHidden(2, True)  # Type
        self.setColumnHidden(3, True)  # Date Modified

        # Connect click event
        self.clicked.connect(self._on_item_clicked)

    def set_workspace(self, folder_path: str):
        """Set active workspace directory for the file tree.

        Args:
            folder_path (str): Path to root directory.
        """
        root_index = self.model.setRootPath(folder_path)
        self.setRootIndex(root_index)

    def refresh_tree(self):
        """Refresh the filesystem view model."""
        current_root = self.model.rootPath()
        if current_root:
            self.model.setRootPath("")
            root_index = self.model.setRootPath(current_root)
            self.setRootIndex(root_index)

    def _on_item_clicked(self, index):
        """Handle tree item selection and emit file_selected signal if a Markdown file is selected."""
        file_path = self.model.filePath(index)
        info = QFileInfo(file_path)
        if info.isFile() and file_path.lower().endswith((".md", ".markdown")):
            self.file_selected.emit(file_path)
