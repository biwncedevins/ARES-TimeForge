"""Shared UI widgets. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


def make_key_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("KeyLabel")
    return label


def make_value_label(text: str = "-", accent: bool = False, ok: bool = False,
                     danger: bool = False) -> QLabel:
    label = QLabel(text)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    if danger:
        label.setObjectName("ValueDanger")
    elif ok:
        label.setObjectName("ValueOk")
    elif accent:
        label.setObjectName("ValueAccent")
    else:
        label.setObjectName("ValueLabel")
    return label


def copy_to_clipboard(text: str) -> None:
    QGuiApplication.clipboard().setText(text)


class KeyValueGrid(QWidget):
    """Dense two-column key/value grid with a monospace value column."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(24)
        self._layout.setVerticalSpacing(6)
        self._layout.setColumnStretch(0, 0)
        self._layout.setColumnStretch(1, 1)
        self._rows: dict[str, QLabel] = {}
        self._index = 0

    def add_row(self, key: str, value_label: QLabel) -> QLabel:
        self._layout.addWidget(make_key_label(key), self._index, 0,
                               Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(value_label, self._index, 1,
                               Qt.AlignmentFlag.AlignTop)
        self._rows[key] = value_label
        self._index += 1
        return value_label

    def add_string_row(self, key: str, text: str = "-",
                       accent: bool = False, ok: bool = False,
                       danger: bool = False) -> QLabel:
        label = make_value_label(text, accent=accent, ok=ok, danger=danger)
        label.setWordWrap(True)
        return self.add_row(key, label)

    def set_value(self, key: str, text: str,
                  accent: bool = False, ok: bool = False,
                  danger: bool = False) -> None:
        label = self._rows[key]
        label.setText(text)
        if danger:
            label.setObjectName("ValueDanger")
        elif ok:
            label.setObjectName("ValueOk")
        elif accent:
            label.setObjectName("ValueAccent")
        else:
            label.setObjectName("ValueLabel")
        label.style().unpolish(label)
        label.style().polish(label)

    def clear_values(self, placeholder: str = "-") -> None:
        for label in self._rows.values():
            label.setText(placeholder)
            label.setObjectName("ValueLabel")
            label.style().unpolish(label)
            label.style().polish(label)


def button_row(parent: QWidget, labels: dict[str, Optional[str]],
               on_click=None) -> list[QPushButton]:
    """Build a horizontal button group. labels maps caption -> objectName."""
    layout = QHBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    buttons: list[QPushButton] = []
    for caption, object_name in labels.items():
        btn = QPushButton(caption)
        if object_name:
            btn.setObjectName(object_name)
        if on_click:
            btn.clicked.connect(lambda *_, b=btn: on_click(b))
        buttons.append(btn)
        layout.addWidget(btn)
    layout.addStretch(1)
    return buttons