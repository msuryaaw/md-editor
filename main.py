"""Main Entry Point for Lightweight Python Markdown Editor

Initializes QApplication, QMainWindow, layout structure, state management, and signal/slot wiring.
Applies GitHub Dark Theme globally.
"""

import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCloseEvent, QFont, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
)

from components.editor_pane import EditorPane
from components.sidebar import SidebarTree
from components.toolbar import MainToolBar
from utils.file_manager import read_file, write_file
from utils.markdown_parser import parse_markdown


GITHUB_DARK_QSS = """
QMainWindow {
    background-color: #0d1117;
    color: #c9d1d9;
}

QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 10pt;
}

/* Toolbar */
QToolBar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
    spacing: 6px;
    padding: 4px;
}

QToolButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 10px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #30363d;
    color: #f0f6fc;
    border-color: #8b949e;
}

QToolButton:checked {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #388bfd;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #161b22;
    color: #c9d1d9;
    border-bottom: 1px solid #30363d;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 10px;
}

QMenuBar::item:selected {
    background-color: #21262d;
    color: #f0f6fc;
    border-radius: 4px;
}

QMenu {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

/* Sidebar Tree */
QTreeView {
    background-color: #161b22;
    color: #c9d1d9;
    border: none;
    border-right: 1px solid #30363d;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
}

QTreeView::item {
    padding: 4px;
    border-radius: 4px;
}

QTreeView::item:hover {
    background-color: #21262d;
    color: #f0f6fc;
}

QTreeView::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    padding: 4px;
    border: none;
    border-bottom: 1px solid #30363d;
}

/* Custom Editor (QTextEdit) */
QTextEdit {
    background-color: #0d1117;
    color: #c9d1d9;
    border: none;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    padding: 12px;
}

/* Custom Preview (QTextBrowser) */
QTextBrowser {
    background-color: #0d1117;
    color: #c9d1d9;
    border: none;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}

/* Splitter */
QSplitter::handle {
    background-color: #30363d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

/* Status Bar */
QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #30363d;
}

/* Dialogs & Input */
QInputDialog, QMessageBox, QFileDialog {
    background-color: #161b22;
    color: #c9d1d9;
}

QLineEdit {
    background-color: #0d1117;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px;
}

QLineEdit:focus {
    border-color: #58a6ff;
}
"""


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MD Editor")
        self.resize(1100, 700)

        # Set Window Icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # State Variables
        self.current_workspace_path: Optional[str] = None
        self.current_file_path: Optional[str] = None
        self.active_view_mode: str = "split"
        self.is_strict_mode: bool = True
        self.is_modified: bool = False

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

        # Security Mode Status Bar Toggle Button
        self.security_btn = QPushButton(self)
        self.security_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.security_btn.clicked.connect(lambda: self.toggle_security_mode())
        self.status_bar.addPermanentWidget(self.security_btn)

        # Initial UI update for security mode
        self.update_security_ui()

    def _setup_menus(self):
        """Configure main application menu bar."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        new_file_action = QAction("&New File", self)
        new_file_action.setShortcut(QKeySequence("Ctrl+N"))
        new_file_action.triggered.connect(self.create_new_file)
        file_menu.addAction(new_file_action)

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

        # Security Menu
        security_menu = menu_bar.addMenu("&Security")

        self.security_menu_action = QAction("🔒 Strict Mode (Offline)", self)
        self.security_menu_action.setCheckable(True)
        self.security_menu_action.setChecked(self.is_strict_mode)
        self.security_menu_action.triggered.connect(self.toggle_security_mode)
        security_menu.addAction(self.security_menu_action)

    def toggle_security_mode(self, checked: Optional[bool] = None):
        """Toggle Security Mode state (Strict Mode vs Standard Mode).

        Args:
            checked (Optional[bool]): If provided, sets strict mode directly; otherwise flips mode.
        """
        if checked is None or not isinstance(checked, bool):
            self.is_strict_mode = not self.is_strict_mode
        else:
            self.is_strict_mode = checked

        self.editor_pane.preview.set_strict_mode(self.is_strict_mode)
        self.update_security_ui()

        # Re-render current content to reflect new security rule
        current_text = self.editor_pane.editor.toPlainText()
        self.on_content_changed(current_text)

    def update_security_ui(self):
        """Update Status Bar button text/style and Menu Action state."""
        if self.is_strict_mode:
            self.security_btn.setText("🔒 Strict Mode (Offline)")
            self.security_btn.setToolTip("Strict Security Mode Active: All HTTP/HTTPS requests blocked")
            self.security_btn.setStyleSheet("""
                QPushButton {
                    background-color: #238636;
                    color: #ffffff;
                    border: 1px solid #2ea043;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #2ea043;
                }
            """)
        else:
            self.security_btn.setText("🌐 Standard Mode (Online Badges)")
            self.security_btn.setToolTip("Standard Mode Active: Remote HTTP/HTTPS images allowed")
            self.security_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9e6a03;
                    color: #ffffff;
                    border: 1px solid #bb8009;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #bb8009;
                }
            """)

        if hasattr(self, "security_menu_action"):
            self.security_menu_action.setChecked(self.is_strict_mode)
            self.security_menu_action.setText(
                "🔒 Strict Mode (Offline)" if self.is_strict_mode else "🌐 Standard Mode (Online Badges)"
            )

    def _setup_shortcuts(self):
        """Configure keyboard shortcuts."""
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self.create_new_file)

        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_file)

    def _connect_signals(self):
        """Connect Signals and Slots across all components."""
        # Toolbar signals
        self.toolbar.new_file_requested.connect(self.create_new_file)
        self.toolbar.open_folder_requested.connect(self.open_workspace_dialog)
        self.toolbar.save_requested.connect(self.save_current_file)
        self.toolbar.mode_changed.connect(self.on_mode_changed)

        # Sidebar file selection signal
        self.sidebar.file_selected.connect(self.load_file)

        # Real-time preview signal: Editor text change -> Markdown parser -> Preview HTML
        self.editor_pane.editor.content_changed.connect(self.on_content_changed)

        # Track text modification for unsaved changes warning
        self.editor_pane.editor.textChanged.connect(self.on_text_modified)

    def update_window_title(self):
        """Update window title reflecting current file path and modified status."""
        base_title = f"{self.current_file_path} - MD Editor" if self.current_file_path else "MD Editor"
        title = f"*{base_title}" if self.is_modified else base_title
        self.setWindowTitle(title)

    def on_text_modified(self):
        """Slot triggered on editor textChanged signal."""
        if not self.is_modified:
            self.is_modified = True
            self.update_window_title()

    def create_new_file(self):
        """Create a new Markdown file in the workspace or target location."""
        if self.current_workspace_path:
            file_name, ok = QInputDialog.getText(
                self,
                "New Markdown File",
                "Masukkan nama file Markdown baru (contoh: notes.md):",
            )
            if not ok or not file_name.strip():
                return

            clean_name = file_name.strip()
            if not clean_name.lower().endswith((".md", ".markdown")):
                clean_name += ".md"

            target_path = os.path.join(self.current_workspace_path, clean_name)
        else:
            target_path, _ = QFileDialog.getSaveFileName(
                self,
                "Buat File Markdown Baru",
                "",
                "Markdown Files (*.md *.markdown)",
            )
            if not target_path:
                return

        try:
            # Create empty file
            write_file(target_path, "")

            # Refresh workspace sidebar tree if active
            if self.current_workspace_path:
                self.sidebar.refresh_tree()

            # Load new file into editor
            self.load_file(target_path)
            self.editor_pane.editor.setFocus()
            self.status_bar.showMessage(f"File baru berhasil dibuat: {target_path}")
        except IOError as err:
            QMessageBox.critical(self, "Error Buat File", str(err))

    def open_workspace_dialog(self):
        """Open file dialog to select a workspace directory."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Pilih Folder Workspace", self.current_workspace_path or ""
        )
        if folder_path:
            self.current_workspace_path = folder_path
            self.sidebar.set_workspace(folder_path)
            self.editor_pane.preview.set_base_dir(folder_path)
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
            self.editor_pane.preview.set_base_dir(os.path.dirname(file_path))

            self.is_modified = False
            self.update_window_title()
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
            self.is_modified = False
            self.update_window_title()
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

    def closeEvent(self, event: QCloseEvent):
        """Intercept window close event to confirm unsaved changes.

        Args:
            event (QCloseEvent): Window close event.
        """
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Konfirmasi Tutup",
                "Dokumen memiliki perubahan yang belum disimpan. Apakah Anda ingin menyimpannya?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
                if not self.is_modified:
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Application main entry point."""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(GITHUB_DARK_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
