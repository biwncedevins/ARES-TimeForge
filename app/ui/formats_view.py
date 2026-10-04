"""Formats reference page. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.formats import FORMATS

HEADERS = ["Format", "Epoch", "Unit", "Typical representation", "Explanation"]


class FormatsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("FORMAT REFERENCE")
        title.setObjectName("SectionLabel")
        root.addWidget(title)

        hint = QLabel(
            "Reference values shown for each supported timestamp format. "
            "Detection uses magnitude, digit-length and date plausibility."
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
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.table.setWordWrap(True)

        self.table.setRowCount(len(FORMATS))
        for i, fmt in enumerate(FORMATS):
            self._set(i, 0, fmt.name)
            self._set(i, 1, fmt.epoch_label)
            self._set(i, 2, fmt.unit_label)
            self._set(i, 3, fmt.typical)
            self._set(i, 4, fmt.explanation)
        root.addWidget(self.table, 1)

    def _set(self, row: int, col: int, text: str) -> None:
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        if col in (0, 1, 2):
            font = item.font()
            item.setFont(font)
        self.table.setItem(row, col, item)