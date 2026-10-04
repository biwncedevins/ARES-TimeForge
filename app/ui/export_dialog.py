"""Export page. TimeForge

Scope: current result | current comparison | full session history.
Format: JSON | CSV | TXT | HTML (all static, local-only files).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.reports import QUALIFIERS, ReportError, default_filename, render


class ExportView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_result: Optional[TimestampResult] = None
        self.current_comparison: Optional[Comparison] = None
        self.history_items: List[TimestampResult] = []
        self._last_path: Optional[str] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("EXPORT REPORT")
        title.setObjectName("SectionLabel")
        root.addWidget(title)

        hint = QLabel(
            "Reports are generated as static local files. No network access "
            "is performed at any stage."
        )
        hint.setObjectName("Explainer")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # scope -------------------------------------------------------------
        scope_label = QLabel("Scope")
        scope_label.setObjectName("KeyLabel")
        root.addWidget(scope_label)
        self.scope_current = QRadioButton("Current result")
        self.scope_comparison = QRadioButton("Current comparison")
        self.scope_history = QRadioButton("Full session history")
        self.scope_current.setChecked(True)
        for radio in (self.scope_current, self.scope_comparison, self.scope_history):
            radio.toggled.connect(self._refresh_hint)
            root.addWidget(radio)

        format_label = QLabel("Format")
        format_label.setObjectName("KeyLabel")
        root.addWidget(format_label)
        self.format_combo = QComboBox()
        for fmt in ("json", "csv", "txt", "html"):
            self.format_combo.addItem(fmt.upper(), fmt)
        self.format_combo.currentIndexChanged.connect(self._refresh_filename)
        root.addWidget(self.format_combo)
        self.format_combo.setMaximumWidth(160)

        file_label = QLabel("Target file")
        file_label.setObjectName("KeyLabel")
        root.addWidget(file_label)
        file_row = QHBoxLayout()
        self.path_field = QLineEdit()
        self.path_field.setText(default_filename("txt"))
        browse = QPushButton("Browse...")
        browse.clicked.connect(self._browse)
        file_row.addWidget(self.path_field, 1)
        file_row.addWidget(browse)
        root.addLayout(file_row)

        self.export_button = QPushButton("Export")
        self.export_button.setObjectName("PrimaryButton")
        self.export_button.clicked.connect(self._do_export)
        root.addWidget(self.export_button)
        self.export_button.setMaximumWidth(160)

        self.status_label = QLabel("Nothing exported yet.")
        self.status_label.setObjectName("ValueLabel")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)

        self._refresh_filename()
        root.addStretch(1)

    # -- helpers -----------------------------------------------------------
    def _selected_scope(self) -> str:
        if self.scope_history.isChecked():
            return "history"
        if self.scope_comparison.isChecked():
            return "comparison"
        return "result"

    def _selected_filename(self) -> str:
        value = self.path_field.text().strip()
        if not value:
            value = default_filename(self.current_format())
        if not Path(value).suffix:
            value += QUALIFIERS[self.current_format()]
        return value

    def current_format(self) -> str:
        return self.format_combo.currentData()

    def _refresh_filename(self, *_args) -> None:
        folder = os.path.dirname(self.path_field.text())
        name = default_filename(self.current_format())
        if folder:
            self.path_field.setText(os.path.join(folder, name))
        else:
            self.path_field.setText(name)

    def _browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export TimeForge report",
            self._selected_filename(),
            "Report files (*"
            + " *".join(f"*{q}" for q in QUALIFIERS.values())
            + ");;All files (*.*)",
        )
        if path:
            self.path_field.setText(path)
            self.export_button.setFocus()

    def _refresh_hint(self, *_args) -> None:
        self.status_label.setText("Select a scope and format, then export.")

    # -- export ------------------------------------------------------------
    def _do_export(self) -> None:
        scope = self._selected_scope()
        results: List[TimestampResult] = []
        comparison: Optional[Comparison] = None

        if scope == "result":
            if self.current_result is None:
                self._set_status(
                    "No result to export — run an analysis first.", error=True
                )
                return
            results = [self.current_result]
        elif scope == "comparison":
            if self.current_comparison is None:
                self._set_status(
                    "No comparison to export — run a comparison first.",
                    error=True,
                )
                return
            comparison = self.current_comparison
        else:
            results = list(self.history_items)
            comparison = self.current_comparison

        try:
            content = render(
                self.current_format(), results, comparison
            )
        except ReportError as exc:
            self._set_status(f"Export failed: {exc.message}", error=True)
            return

        target = self._selected_filename()
        try:
            Path(target).write_text(content, encoding="utf-8")
        except OSError as exc:
            self._set_status(
                f"Export failed: could not write {target}. Reason: {exc}",
                error=True,
            )
            return

        self._last_path = target
        self._set_status(f"Exported {len(content)} bytes to {target}")

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status_label.setText(text)
        self.status_label.setObjectName(
            "ValueDanger" if error else "ValueLabel"
        )
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def reset(self) -> None:
        self.current_result = None
        self.current_comparison = None
        self.history_items = []
        self.status_label.setText("Nothing exported yet.")