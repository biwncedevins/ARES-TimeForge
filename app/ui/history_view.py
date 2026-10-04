"""Session history page. TimeForge"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.timestamp_result import TimestampResult
from app.ui.common import copy_to_clipboard

HEADERS = ["#", "Input", "Format", "Confidence", "UTC", "Local"]


class HistoryView(QWidget):
    loadRequested = Signal(str)
    statusMessage = Signal(str)
    historyChanged = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._items: List[TimestampResult] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("SESSION HISTORY")
        title.setObjectName("SectionLabel")
        root.addWidget(title)
        hint = QLabel(
            "History is session-only and cleared when the application "
            "closes. It is never persisted to disk."
        )
        hint.setObjectName("Explainer")
        hint.setWordWrap(True)
        root.addWidget(hint)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self._load_selected)
        root.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        for caption, handler in (
            ("Load in Analyzer", self._load_selected),
            ("Copy UTC", lambda: self._copy(0)),
            ("Copy Local", lambda: self._copy(1)),
            ("Copy Full Result", lambda: self._copy(2)),
            ("Clear", self._clear_history),
        ):
            btn = QPushButton(caption)
            btn.clicked.connect(handler)
            buttons.addWidget(btn)
        buttons.addStretch(1)
        root.addLayout(buttons)

    # -- model -------------------------------------------------------------
    def add(self, result: TimestampResult) -> None:
        self._items.append(result)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._set_cell(row, 0, str(row + 1))
        self._set_cell(row, 1, result.raw_value)
        self._set_cell(row, 2, result.format_name)
        self._set_cell(row, 3, f"{result.confidence}/100 ({result.confidence_level})")
        self._set_cell(row, 4, result.utc_str)
        self._set_cell(row, 5, result.local_str)
        self.historyChanged.emit(len(self._items))
        self.statusMessage.emit(
            f"History: {len(self._items)} entr{'y' if len(self._items) == 1 else 'ies'}"
        )

    def _set_cell(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        self.table.setItem(row, col, item)

    def _selected_results(self) -> List[TimestampResult]:
        rows = sorted({index.row() for index in self.table.selectedIndexes()})
        return [self._items[r] for r in rows if 0 <= r < len(self._items)]

    # -- actions -----------------------------------------------------------
    def _load_selected(self, *_args) -> None:
        results = self._selected_results()
        if not results:
            self.statusMessage.emit("Select a history row to load")
            return
        self.loadRequested.emit(results[0].raw_value)

    def _copy(self, mode: int) -> None:
        results = self._selected_results()
        if not results:
            self.statusMessage.emit("Select a history row to copy")
            return
        target = results[0]
        if mode == 0:
            copy_to_clipboard(target.utc_str)
        elif mode == 1:
            copy_to_clipboard(target.local_str)
        else:
            copy_to_clipboard(target.explanation)
        self.statusMessage.emit("History entry copied")

    def _clear_history(self) -> None:
        self._items.clear()
        self.table.setRowCount(0)
        self.historyChanged.emit(0)
        self.statusMessage.emit("History cleared")

    def count(self) -> int:
        return len(self._items)