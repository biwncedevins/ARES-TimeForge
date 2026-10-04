"""Compare page. TimeForge"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core import timezone as tzutil
from app.core.pipeline import AnalysisError, Pipeline
from app.models.comparison import Comparison
from app.models.timestamp_result import TimestampResult
from app.ui.common import KeyValueGrid, copy_to_clipboard

A_PLACEHOLDER = "Timestamp A — e.g. 1716201234567"
B_PLACEHOLDER = "Timestamp B — e.g. 133432140000000000"


class CompareView(QWidget):
    comparisonDone = Signal(object)
    statusMessage = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.pipeline = Pipeline()
        self._comparison: Optional[Comparison] = None
        self._a: Optional[TimestampResult] = None
        self._b: Optional[TimestampResult] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("COMPARE TIMESTAMPS")
        title.setObjectName("SectionLabel")
        root.addWidget(title)

        inputs = QHBoxLayout()
        inputs.setSpacing(12)

        a_box = QVBoxLayout()
        a_label = QLabel("Timestamp A")
        a_label.setObjectName("KeyLabel")
        a_box.addWidget(a_label)
        self.a_field = QLineEdit()
        self.a_field.setObjectName("InputField")
        self.a_field.setPlaceholderText(A_PLACEHOLDER)
        a_box.addWidget(self.a_field)
        inputs.addLayout(a_box, 1)

        b_box = QVBoxLayout()
        b_label = QLabel("Timestamp B")
        b_label.setObjectName("KeyLabel")
        b_box.addWidget(b_label)
        self.b_field = QLineEdit()
        self.b_field.setObjectName("InputField")
        self.b_field.setPlaceholderText(B_PLACEHOLDER)
        b_box.addWidget(self.b_field)
        inputs.addLayout(b_box, 1)
        root.addLayout(inputs)

        controls = QHBoxLayout()
        self.compare_button = QPushButton("Compare")
        self.compare_button.setObjectName("PrimaryButton")
        self.compare_button.clicked.connect(self.run_compare)
        self.swap_button = QPushButton("Swap A <-> B")
        self.swap_button.clicked.connect(self._swap)
        controls.addWidget(self.compare_button)
        controls.addWidget(self.swap_button)
        controls.addStretch(1)
        tz_label = QLabel("Timezone")
        tz_label.setObjectName("KeyLabel")
        controls.addWidget(tz_label)
        self.tz_combo = QComboBox()
        self.tz_combo.addItems(tzutil.PRESET_ZONES)
        self.tz_combo.setEditable(True)
        self.tz_combo.setCurrentText("Local")
        self.tz_combo.setFixedWidth(200)
        controls.addWidget(self.tz_combo)
        root.addLayout(controls)

        self.error_label = QLabel()
        self.error_label.setObjectName("ValueDanger")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        root.addWidget(self.error_label)

        result_title = QLabel("RESULT")
        result_title.setObjectName("SectionLabel")
        root.addWidget(result_title)

        self.grid = KeyValueGrid()
        self.grid.add_string_row("A INPUT")
        self.grid.add_string_row("A FORMAT")
        self.grid.add_string_row("A UTC")
        self.grid.add_string_row("A LOCAL")
        self.grid.add_string_row("B INPUT")
        self.grid.add_string_row("B FORMAT")
        self.grid.add_string_row("B UTC")
        self.grid.add_string_row("B LOCAL")
        self.grid.add_string_row("RELATION", accent=True)
        self.grid.add_string_row("DIFFERENCE", accent=True)
        self.grid.add_string_row("NOTES")
        root.addWidget(self.grid, 1)

        buttons = QHBoxLayout()
        self.copy_result = QPushButton("Copy Comparison Result")
        self.copy_result.setEnabled(False)
        self.copy_result.clicked.connect(self._copy)
        buttons.addWidget(self.copy_result)
        buttons.addStretch(1)
        root.addLayout(buttons)

        root.addStretch(1)

    # -- actions ----------------------------------------------------------
    def current_timezone(self) -> str:
        text = self.tz_combo.currentText().strip()
        return text if text else "Local"

    def run_compare(self) -> None:
        a_raw = self.a_field.text().strip()
        b_raw = self.b_field.text().strip()
        if not a_raw or not b_raw:
            self._show_error(
                "Comparison failed.\nReason: both timestamp values are required."
            )
            return
        self._clear_error()
        try:
            a = self.pipeline.analyze(a_raw, self.current_timezone())
            b = self.pipeline.analyze(b_raw, self.current_timezone())
            comparison = self.pipeline.compare(a_raw, b_raw, self.current_timezone())
        except AnalysisError as exc:
            self._show_error(exc.message)
            return
        except tzutil.TimeZoneError as exc:
            self._show_error(f"Comparison failed.\nReason: {exc.message}")
            return

        self._a, self._b = a, b
        self._comparison = comparison
        self._populate(a, b, comparison)
        self.comparisonDone.emit(comparison)
        self.statusMessage.emit(
            f"Comparison OK — {comparison.relation}, diff {comparison.difference}"
        )

    def _populate(self, a, b, c) -> None:
        self.grid.set_value("A INPUT", a.raw_value)
        self.grid.set_value("A FORMAT", a.format_name)
        self.grid.set_value("A UTC", a.utc_str)
        self.grid.set_value("A LOCAL", a.local_str)
        self.grid.set_value("B INPUT", b.raw_value)
        self.grid.set_value("B FORMAT", b.format_name)
        self.grid.set_value("B UTC", b.utc_str)
        self.grid.set_value("B LOCAL", b.local_str)
        self.grid.set_value("RELATION", c.relation, accent=True)
        self.grid.set_value("DIFFERENCE", c.difference, accent=True)
        self.grid.set_value("NOTES", " | ".join(c.notes) if c.notes else "-")
        self.copy_result.setEnabled(True)

    def _swap(self) -> None:
        a_text = self.a_field.text()
        b_text = self.b_field.text()
        self.a_field.setText(b_text)
        self.b_field.setText(a_text)

    def _copy(self) -> None:
        if self._comparison is None:
            return
        c = self._comparison
        block = (
            f"A ({c.a_format}): {c.a_utc}  [{c.a_local}]\n"
            f"B ({c.b_format}): {c.b_utc}  [{c.b_local}]\n"
            f"Relation: {c.relation}\n"
            f"Difference: {c.difference}"
        )
        copy_to_clipboard(block)
        self.statusMessage.emit("Comparison copied")

    def _show_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.show()

    def _clear_error(self) -> None:
        self.error_label.hide()

    def reset(self) -> None:
        self.a_field.clear()
        self.b_field.clear()
        self.grid.clear_values("-")
        self.copy_result.setEnabled(False)
        self._clear_error()