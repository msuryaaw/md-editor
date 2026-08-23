import os
from PyQt6.QtCore import QDir, QFileInfo, Qt, pyqtSignal
from PyQt6.QtGui import QFileSystemModel, QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtWidgets import (
    QFileIconProvider,
    QHeaderView,
    QInputDialog,
    QMenu,
    QMessageBox,
    QTreeView,
)


class MarkdownFileIconProvider(QFileIconProvider):
    """Custom Icon Provider to draw a distinct Markdown icon for .md / .markdown files."""

    def __init__(self):
        super().__init__()
        self._md_icon = self._create_md_icon()

    def _create_md_icon(self) -> QIcon:
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background badge
        painter.setBrush(QColor("#1f6feb"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 16, 16, 3, 3)

        # Draw "M" text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")
        painter.end()

        return QIcon(pixmap)

    def icon(self, type_or_info):
        if isinstance(type_or_info, QFileInfo):
            if type_or_info.isFile() and type_or_info.suffix().lower() in ["md", "markdown"]:
                return self._md_icon
        return super().icon(type_or_info)


class SidebarTree(QTreeView):
    """File explorer sidebar filtered for Markdown files with context menu and custom icons."""

    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = QFileSystemModel(self)
        self.model.setIconProvider(MarkdownFileIconProvider())
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

        # Enable Custom Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

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

    def _show_context_menu(self, position):
        """Show context menu for selected sidebar file/folder."""
        index = self.indexAt(position)
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        info = QFileInfo(file_path)

        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")

        action = menu.exec(self.viewport().mapToGlobal(position))

        if action == rename_action:
            self._rename_file(file_path, info)
        elif action == delete_action:
            self._delete_file(file_path, info)

    def _rename_file(self, file_path: str, info: QFileInfo):
        old_name = info.fileName()
        new_name, ok = QInputDialog.getText(
            self,
            "Rename File",
            "Masukkan nama baru:",
            text=old_name,
        )
        if not ok or not new_name.strip() or new_name == old_name:
            return

        new_name = new_name.strip()
        dir_path = info.absolutePath()
        new_path = os.path.join(dir_path, new_name)

        try:
            os.rename(file_path, new_path)
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error Rename", f"Gagal merename file:\n{str(e)}")

    def _delete_file(self, file_path: str, info: QFileInfo):
        reply = QMessageBox.question(
            self,
            "Hapus File",
            f"Apakah Anda yakin ingin menghapus '{info.fileName()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if info.isDir():
                    os.rmdir(file_path)
                else:
                    os.remove(file_path)
                self.refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error Delete", f"Gagal menghapus file:\n{str(e)}")

