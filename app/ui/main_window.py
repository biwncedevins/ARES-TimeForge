"""Main application window. TimeForge"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.ui.about_view import AboutView
from app.ui.analyzer_view import AnalyzerView
from app.ui.compare_view import CompareView
from app.ui.export_dialog import ExportView
from app.ui.formats_view import FormatsView
from app.ui.history_view import HistoryView
from app.ui.sidebar import Sidebar
from app.ui.topbar import TopBar
from app.utils.resources import icon_path


class MainWindow(QMainWindow):
    """Root window: topbar + (sidebar + QStackedWidget) + status bar."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.history_items: List[TimestampResult] = []
        self._building: bool = True

        self.setWindowTitle("TimeForge — Forensic Timestamp Lab")
        self.setWindowIcon(QIcon(str(icon_path())))
        self.resize(1120, 740)
        self.setMinimumSize(880, 560)

        from PySide6.QtWidgets import QApplication

        _app = QApplication.instance()
        if _app is not None and not _app.styleSheet().strip():
            from app.ui.styles import STYLESHEET

            _app.setStyleSheet(STYLESHEET)

        central = QWidget()
        central.setObjectName("AppRoot")
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.topbar = TopBar()
        outer.addWidget(self.topbar)

        middle = QWidget()
        middle.setObjectName("PanelInner")
        middle_layout = QHBoxLayout(middle)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)

        self.sidebar = Sidebar()
        middle_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        middle_layout.addWidget(self.stack, 1)
        outer.addWidget(middle, 1)

        self.setCentralWidget(central)

        self.analyzer_view = AnalyzerView()
        self.compare_view = CompareView()
        self.formats_view = FormatsView()
        self.history_view = HistoryView()
        self.export_view = ExportView()
        self.about_view = AboutView()
        for view in (
            self.analyzer_view,
            self.compare_view,
            self.formats_view,
            self.history_view,
            self.export_view,
            self.about_view,
        ):
            self.stack.addWidget(view)

        self._wire_signals()
        self._install_shortcuts()

        self.statusBar().setSizeGripEnabled(True)
        self.statusBar().showMessage("TimeForge ready — offline", 4000)
        self._building = False
        self.sidebar.select(0)

    # -- wiring ------------------------------------------------------------
    def _wire_signals(self) -> None:
        self.sidebar.pageRequested.connect(self._go_page)
        self.stack.currentChanged.connect(self._sync_sidebar)

        self.topbar.newRequested.connect(self._action_new)
        self.topbar.analyzeRequested.connect(self._action_analyze)
        self.topbar.compareRequested.connect(
            lambda: self._go_page(1)
        )
        self.topbar.exportRequested.connect(
            lambda: self._go_page(4)
        )

        self.analyzer_view.analysisDone.connect(self._on_analyzed)
        self.analyzer_view.statusMessage.connect(self._status)
        self.compare_view.comparisonDone.connect(self._on_compared)
        self.compare_view.statusMessage.connect(self._status)
        self.history_view.loadRequested.connect(self.analyzer_view.load_value)
        self.history_view.historyChanged.connect(self._on_history_changed)
        self.history_view.statusMessage.connect(self._status)

    def _go_page(self, page_index: int) -> None:
        self.stack.setCurrentIndex(page_index)
        if not self._building:
            self.sidebar.select(page_index)

    def _sync_sidebar(self, index: int) -> None:
        if not self._building:
            self.sidebar.select(index)

    def _status(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)

    # -- data wiring -------------------------------------------------
    def _on_analyzed(self, result: TimestampResult) -> None:
        self.history_items.append(result)
        self.history_view.add(result)
        self.export_view.current_result = result

    def _on_compared(self, comparison: Comparison) -> None:
        self.export_view.current_comparison = comparison

    def _on_history_changed(self, count: int) -> None:
        self.export_view.history_items = list(self.history_items)

    # -- top actions -------------------------------------------------
    def _action_new(self) -> None:
        self.analyzer_view.reset()
        self.compare_view.reset()
        self.export_view.reset()
        self.history_items.clear()
        self._go_page(0)
        self.analyzer_view.input_field.setFocus()
        self._status("New session")

    def _action_analyze(self) -> None:
        self._go_page(0)
        self.analyzer_view.input_field.setFocus()
        self.analyzer_view.run_analysis()

    def _action_focus_input(self) -> None:
        self._go_page(0)
        self.analyzer_view.input_field.setFocus()

    def _action_copy_utc(self) -> None:
        if self.analyzer_view._result is not None:
            from app.ui.common import copy_to_clipboard

            copy_to_clipboard(self.analyzer_view._result.utc_str)
            self._status("Copied UTC")

    def _action_paste_analyze(self) -> None:
        clipboard = QGuiApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            self._status("Clipboard is empty")
            return
        self.analyzer_view.input_field.setText(text)
        self._go_page(0)
        self.analyzer_view.run_analysis()

    # -- shortcuts ----------------------------------------------------
    def _install_shortcuts(self) -> None:
        self._sc = [
            self._shortcut("Ctrl+N", self._action_new),
            self._shortcut("Ctrl+Enter", self._action_analyze),
            self._shortcut("Ctrl+Shift+C", self._action_copy_utc),
            self._shortcut("Ctrl+E", lambda: self._go_page(4)),
            self._shortcut("Ctrl+F", self._action_focus_input),
        ]
        paste = QAction("Paste and Analyze", self)
        paste.setShortcut(QKeySequence("Ctrl+V"))
        paste.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        paste.triggered.connect(self._action_paste_analyze)
        self.addAction(paste)

    def _shortcut(self, sequence: str, slot) -> QAction:
        action = QAction(self)
        action.setShortcut(QKeySequence(sequence))
        action.triggered.connect(slot)
        self.addAction(action)
        return action