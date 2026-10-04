"""Sidebar navigation. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

ANALYZER = 0
COMPARE = 1
FORMATS = 2
HISTORY = 3
EXPORT = 4
ABOUT = 5

_PAGES = [
    (ANALYZER, "Analyzer"),
    (COMPARE, "Compare"),
    (FORMATS, "Formats"),
    (HISTORY, "History"),
    (EXPORT, "Export"),
    (ABOUT, "About"),
]


class Sidebar(QFrame):
    pageRequested = Signal(int)

    def __init__(self, parent: Optional[QFrame] = None):
        super().__init__(parent)
        self.setObjectName("SideBar")
        self.setFixedWidth(176)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(2)

        title = QLabel("TIMEFORGE")
        title.setObjectName("BrandTitle")
        layout.addSpacing(4)
        layout.addWidget(title)
        tagline = QLabel("FORENSIC\nTIMESTAMP LAB")
        tagline.setObjectName("BrandTagline")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)
        layout.addSpacing(16)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[int, QPushButton] = {}

        for page_index, label in _PAGES:
            btn = QPushButton(label)
            btn.setObjectName("SideButton")
            btn.setCheckable(True)
            btn.setCursor(btn.cursor().shape())
            self._group.addButton(btn, page_index)
            self._buttons[page_index] = btn
            layout.addWidget(btn)

        layout.addStretch(1)

        self._group.buttonClicked.connect(self._on_clicked)

    def _on_clicked(self, button: QPushButton) -> None:
        self.pageRequested.emit(self._group.id(button))

    def select(self, page_index: int) -> None:
        btn = self._buttons.get(page_index)
        if btn is not None:
            btn.setChecked(True)

    def current(self) -> int:
        return self._group.checkedId() if self._group.checkedButton() else ANALYZER