"""About page. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.utils.resources import app_version


class AboutView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("ABOUT")
        title.setObjectName("SectionLabel")
        root.addWidget(title)

        app_name = QLabel("TimeForge")
        app_name.setObjectName("BrandTitle")
        root.addWidget(app_name)

        tag = QLabel("FORENSIC TIMESTAMP LAB")
        tag.setObjectName("BrandTagline")
        root.addWidget(tag)

        version = QLabel(f"Version {app_version()}")
        version.setObjectName("Explainer")
        root.addWidget(version)

        body = QLabel(
            "TimeForge converts raw timestamp values into clear timestamp "
            "interpretations with format detection, conversion, timezone "
            "localization, verification, comparison and static export.\n\n"
            "Design principles:\n"
            "  • Offline-first: zero network access.\n"
            "  • Static detection is heuristic; ambiguous input is reported "
            "as alternatives, never as false certainty.\n"
            "  • The raw input value is always preserved.\n"
            "  • Input is treated strictly as data — it is never executed.\n\n"
            "Supported formats: Unix seconds / milliseconds / microseconds / "
            "nanoseconds, Windows FILETIME, .NET Ticks, Chromium and WebKit "
            "timestamps, Mac Absolute Time, OLE Automation Date, plus hex "
            "representations of these formats."
        )
        body.setObjectName("Explainer")
        body.setWordWrap(True)
        root.addWidget(body)

        sec = QLabel(
            "Security: fully offline. No subprocesses, no PowerShell, no "
            "shell scripts, no browser requests, no external services."
        )
        sec.setObjectName("Explainer")
        sec.setWordWrap(True)
        root.addWidget(sec)

        root.addStretch(1)