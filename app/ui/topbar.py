"""Top action bar. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.utils.resources import icon_path


class TopBar(QFrame):
    newRequested = Signal()
    analyzeRequested = Signal()
    compareRequested = Signal()
    exportRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        brand_icon = QLabel()
        brand_icon.setPixmap(QIcon(str(icon_path())).pixmap(28, 28))
        layout.addWidget(brand_icon)

        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)
        title = QLabel("TimeForge")
        title.setObjectName("BrandTitle")
        tagline = QLabel("FORENSIC TIMESTAMP LAB")
        tagline.setObjectName("BrandTagline")
        brand_box.addWidget(title)
        brand_box.addWidget(tagline)
        layout.addLayout(brand_box)

        layout.addStretch(1)

        self._buttons: dict[str, QPushButton] = {}
        for caption, obj, slot in (
            ("New", "TopButton", self.newRequested),
            ("Analyze", "TopButton", self.analyzeRequested),
            ("Compare", "TopButton", self.compareRequested),
            ("Export", "TopButton", self.exportRequested),
        ):
            btn = QPushButton(caption)
            btn.setObjectName(obj)
            btn.setCursor(btn.cursor().shape())
            btn.clicked.connect(slot)
            self._buttons[caption] = btn
            layout.addWidget(btn)