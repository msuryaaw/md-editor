"""Main Entry Point for Lightweight Python Markdown Editor

Initializes QApplication, QMainWindow, layout structure, state management, and signal/slot wiring.
"""

import sys
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
)

from components.editor_pane import EditorPane
from components.sidebar import SidebarTree
from components.toolbar import MainToolBar
from utils.file_manager import read_file, write_file
from utils.markdown_parser import parse_markdown


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Markdown Editor")
        self.resize(1100, 700)

        # State Variables
        self.current_workspace_path: Optional[str] = None
        self.current_file_path: Optional[str] = None
        self.active_view_mode: str = "split"

        # Initialize User Interface
        self._init_ui()
        self._setup_menus()
        self._setup_shortcuts()
        self._connect_signals()

    def _init_ui(self):
        """Build main layout and child components."""
        # Top Toolbar
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # Horizontal Splitter (Sidebar | EditorPane)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal, self)

        self.sidebar = SidebarTree(self.main_splitter)
        self.editor_pane = EditorPane(self.main_splitter)

        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.addWidget(self.editor_pane)

        # Set initial splitter proportions (Sidebar: 220px, EditorPane: rest)
        self.main_splitter.setSizes([220, 880])
        self.setCentralWidget(self.main_splitter)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Siap - Buka folder workspace untuk memulai")

    def _setup_menus(self):
        """Configure main application menu bar."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        open_folder_action = QAction("&Open Folder...", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        open_folder_action.triggered.connect(self.open_workspace_dialog)
        file_menu.addAction(open_folder_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")

        code_view_action = QAction("&Code Mode", self)
        code_view_action.triggered.connect(lambda: self.on_mode_changed("code"))
        view_menu.addAction(code_view_action)

        split_view_action = QAction("&Split Mode", self)
        split_view_action.triggered.connect(lambda: self.on_mode_changed("split"))
        view_menu.addAction(split_view_action)

        preview_view_action = QAction("&Preview Mode", self)
        preview_view_action.triggered.connect(lambda: self.on_mode_changed("preview"))
        view_menu.addAction(preview_view_action)

    def _setup_shortcuts(self):
        """Configure keyboard shortcuts."""
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_file)

    def _connect_signals(self):
        """Connect Signals and Slots across all components."""
        # Toolbar signals
        self.toolbar.open_folder_requested.connect(self.open_workspace_dialog)
        self.toolbar.save_requested.connect(self.save_current_file)
        self.toolbar.mode_changed.connect(self.on_mode_changed)

        # Sidebar file selection signal
        self.sidebar.file_selected.connect(self.load_file)

        # Real-time preview signal: Editor text change -> Markdown parser -> Preview HTML
        self.editor_pane.editor.content_changed.connect(self.on_content_changed)

    def open_workspace_dialog(self):
        """Open file dialog to select a workspace directory."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Pilih Folder Workspace", self.current_workspace_path or ""
        )
        if folder_path:
            self.current_workspace_path = folder_path
            self.sidebar.set_workspace(folder_path)
            self.status_bar.showMessage(f"Workspace aktif: {folder_path}")

    def load_file(self, file_path: str):
        """Load Markdown text file into the editor.

        Args:
            file_path (str): Target Markdown file path.
        """
        try:
            content = read_file(file_path)
            self.current_file_path = file_path
            self.editor_pane.editor.setText(content)

            self.setWindowTitle(f"Markdown Editor - {file_path}")
            self.status_bar.showMessage(f"Membuka berkas: {file_path}")

            # Initial preview rendering
            self.on_content_changed(content)
        except IOError as err:
            QMessageBox.critical(self, "Error Membaca File", str(err))
            self.status_bar.showMessage(f"Gagal membuka berkas: {file_path}")

    def save_current_file(self):
        """Save current editor content to disk."""
        if not self.current_file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Simpan File Markdown",
                self.current_workspace_path or "",
                "Markdown Files (*.md *.markdown)",
            )
            if not file_path:
                return
            self.current_file_path = file_path

        content = self.editor_pane.editor.toPlainText()
        try:
            write_file(self.current_file_path, content)
            self.setWindowTitle(f"Markdown Editor - {self.current_file_path}")
            self.status_bar.showMessage(f"Berhasil menyimpan: {self.current_file_path}")
        except IOError as err:
            QMessageBox.critical(self, "Error Menyimpan File", str(err))
            self.status_bar.showMessage(f"Gagal menyimpan berkas: {self.current_file_path}")

    def on_content_changed(self, text: str):
        """Parse raw Markdown string into HTML and render in preview widget.

        Args:
            text (str): Raw Markdown string.
        """
        html = parse_markdown(text)
        self.editor_pane.preview.render_html(html)

    def on_mode_changed(self, mode_name: str):
        """Switch application view mode ('code', 'split', 'preview').

        Args:
            mode_name (str): View mode identifier.
        """
        self.active_view_mode = mode_name
        self.editor_pane.set_mode(mode_name)
        self.toolbar.set_active_mode(mode_name)
        self.status_bar.showMessage(f"Mode tampilan: {mode_name.upper()}")


def main():
    """Application main entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
