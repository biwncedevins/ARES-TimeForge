"""Analyzer page. TimeForge"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.pipeline import AnalysisError, Pipeline
from app.core import timezone as tzutil
from app.models.timestamp_result import TimestampResult
from app.ui.common import (
    KeyValueGrid,
    copy_to_clipboard,
    make_value_label,
)

PLACEHOLDER = (
    "1716201234567\n"
    "or 0x01D71F0E96F4EBF0\n"
    "or 1716201234 (Unix seconds)\n"
    "or 45221.5 (OLE)"
)


class AnalyzerView(QWidget):
    analysisDone = Signal(object)
    statusMessage = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.pipeline = Pipeline()
        self._result: Optional[TimestampResult] = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        input_label = QLabel("ENTER TIMESTAMP VALUE")
        input_label.setObjectName("SectionLabel")
        root.addWidget(input_label)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("InputField")
        self.input_field.setPlaceholderText(PLACEHOLDER)
        self.input_field.returnPressed.connect(self.run_analysis)
        root.addWidget(self.input_field)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.auto_button = QPushButton("Auto Detect")
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setObjectName("PrimaryButton")
        self.auto_button.clicked.connect(self.run_auto)
        self.analyze_button.clicked.connect(self.run_analysis)
        controls.addWidget(self.auto_button)
        controls.addWidget(self.analyze_button)
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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        container = QWidget()
        container.setObjectName("PanelInner")
        box = QVBoxLayout(container)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(10)

        result_label = QLabel("ANALYSIS RESULT")
        result_label.setObjectName("SectionLabel")
        box.addWidget(result_label)

        self.grid = KeyValueGrid()
        self.grid.add_string_row("INPUT")
        self.grid.add_string_row("NORMALIZED")
        self.grid.add_string_row("DETECTED FORMAT", accent=True)
        self.grid.add_string_row("CONFIDENCE")
        self.grid.add_string_row("PRECISION")
        self.grid.add_string_row("UTC")
        self.grid.add_string_row("LOCAL TIME")
        self.grid.add_string_row("TIMEZONE")
        self.grid.add_string_row("OFFSET")
        self.grid.add_string_row("EPOCH")
        self.grid.add_string_row("UNIT")
        self.grid.add_string_row("VERIFICATION", accent=True)
        self.grid.add_string_row("WARNINGS")
        self.grid.add_string_row("EXPLANATION")
        box.addWidget(self.grid)

        self.copy_row_host = QWidget()
        copy_layout = QHBoxLayout(self.copy_row_host)
        copy_layout.setContentsMargins(0, 0, 0, 0)
        self.copy_utc = QPushButton("Copy UTC")
        self.copy_local = QPushButton("Copy Local")
        self.copy_full = QPushButton("Copy Full Result")
        for btn in (self.copy_utc, self.copy_local, self.copy_full):
            btn.setEnabled(False)
            copy_layout.addWidget(btn)
        copy_layout.addStretch(1)
        box.addWidget(self.copy_row_host)

        alt_label = QLabel("POSSIBLE INTERPRETATIONS")
        alt_label.setObjectName("SectionLabel")
        box.addWidget(alt_label)

        self.alternatives_container = QWidget()
        self.alternatives_container.setObjectName("PanelInner")
        self._alt_layout = QVBoxLayout(self.alternatives_container)
        self._alt_layout.setContentsMargins(0, 0, 0, 0)
        self._alt_layout.setSpacing(4)
        box.addWidget(self.alternatives_container)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        self.grid.clear_values("-")
        self._set_alternatives_empty()

        self.copy_utc.clicked.connect(lambda: self._copy("utc"))
        self.copy_local.clicked.connect(lambda: self._copy("local"))
        self.copy_full.clicked.connect(lambda: self._copy("full"))

    # -- actions ----------------------------------------------------------
    def current_timezone(self) -> str:
        text = self.tz_combo.currentText().strip()
        return text if text else "Local"

    def run_auto(self) -> None:
        self.run_analysis(auto=True)

    def run_analysis(self, auto: bool = False) -> None:
        raw = self.input_field.text().strip()
        if not raw:
            self._show_error("Analysis failed.\nReason: input is empty.")
            self.statusMessage.emit("No input to analyze")
            return
        self._clear_error()
        try:
            result = self.pipeline.analyze(raw, self.current_timezone())
        except AnalysisError as exc:
            self._show_error(exc.message)
            self.grid.clear_values("-")
            self._set_alternatives_empty()
            for btn in (self.copy_utc, self.copy_local, self.copy_full):
                btn.setEnabled(False)
            self.statusMessage.emit("Analysis failed")
            return
        except tzutil.TimeZoneError as exc:
            self._show_error(f"Analysis failed.\nReason: {exc.message}")
            self.statusMessage.emit("Invalid timezone")
            return

        self._result = result
        self._populate(result)
        self.analysisDone.emit(result)
        self.statusMessage.emit(
            f"OK — {result.format_name}, {result.confidence}/100 "
            f"({result.confidence_level})"
        )

    def _populate(self, r: TimestampResult) -> None:
        self.grid.set_value("INPUT", r.raw_value)
        self.grid.set_value("NORMALIZED", r.normalized_value)
        self.grid.set_value("DETECTED FORMAT", r.format_name, accent=True)
        self.grid.set_value(
            "CONFIDENCE",
            f"{r.confidence}/100 ({r.confidence_level})",
            accent=r.confidence >= 45,
        )
        self.grid.set_value("PRECISION", r.precision_note)
        self.grid.set_value("UTC", r.utc_str)
        self.grid.set_value("LOCAL TIME", r.local_str)
        self.grid.set_value("TIMEZONE", r.timezone_name)
        self.grid.set_value("OFFSET", r.local_offset)
        self.grid.set_value("EPOCH", r.epoch_label)
        self.grid.set_value("UNIT", r.unit_label)
        self.grid.set_value(
            "VERIFICATION",
            r.verification.status,
            ok=r.verification.status == "VALID",
            accent=r.verification.status == "WARNING",
            danger=r.verification.status == "INVALID",
        )
        self.grid.set_value(
            "WARNINGS",
            " | ".join(r.warnings) if r.warnings else "None",
            danger=bool(r.warnings),
        )
        self.grid.set_value("EXPLANATION", r.explanation)
        self._render_alternatives(r.alternatives)
        for btn in (self.copy_utc, self.copy_local, self.copy_full):
            btn.setEnabled(True)

    def _render_alternatives(self, alts: List) -> None:
        self._clear_alternatives()
        if not alts:
            hint = make_value_label("None — interpretation is unambiguous.")
            hint.setObjectName("ValueLabel")
            hint.setText("None — interpretation is unambiguous.")
            self._alt_layout.addWidget(hint)
            return

        header = QHBoxLayout()
        header.setSpacing(16)
        for text, stretch in (
            ("FORMAT", 0),
            ("RESULT (UTC)", 0),
            ("CONFIDENCE", 0),
            ("REASON", 1),
        ):
            lab = QLabel(text)
            lab.setObjectName("KeyLabel")
            if stretch:
                header.addWidget(lab, stretch)
            else:
                header.addWidget(lab)
        header_wrap = QWidget()
        header_wrap.setLayout(header)
        self._alt_layout.addWidget(header_wrap)

        for cand in alts:
            row = QHBoxLayout()
            row.setSpacing(16)
            fmt = make_value_label(cand.format_name)
            res = make_value_label(
                cand.utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                + (
                    f".{cand.utc_dt.microsecond:06d}"
                    f"{cand.nanosecond_remainder:03d}"
                    if cand.nanosecond_remainder
                    else f".{cand.utc_dt.microsecond:06d}"
                )
            )
            conf = make_value_label(f"{cand.confidence}/100 ({cand.confidence_level})")
            reason = make_value_label(" ".join(cand.reasons[:3]))
            reason.setWordWrap(True)
            row.addWidget(fmt, 0)
            row.addWidget(res, 0)
            row.addWidget(conf, 0)
            row.addWidget(reason, 1)
            wrap = QWidget()
            wrap.setLayout(row)
            self._alt_layout.addWidget(wrap)

    def _clear_alternatives(self) -> None:
        while self._alt_layout.count():
            item = self._alt_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _set_alternatives_empty(self) -> None:
        self._clear_alternatives()
        hint = QLabel("Enter a value above and run detection to list all "
                      "plausible interpretations.")
        hint.setObjectName("EmptyHint")
        self._alt_layout.addWidget(hint)

    def _show_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.show()

    def _clear_error(self) -> None:
        self.error_label.hide()

    def _copy(self, which: str) -> None:
        r = self._result
        if r is None:
            return
        if which == "utc":
            copy_to_clipboard(r.utc_str)
        elif which == "local":
            copy_to_clipboard(r.local_str)
        else:
            block = (
                f"Input     : {r.raw_value}\n"
                f"Formatted : {r.normalized_value}\n"
                f"Format    : {r.format_name}\n"
                f"Confidence: {r.confidence}/100 ({r.confidence_level})\n"
                f"UTC       : {r.utc_str}\n"
                f"Local     : {r.local_str}\n"
                f"Timezone  : {r.timezone_name}\n"
                f"Offset    : {r.local_offset}\n"
                f"Epoch     : {r.epoch_label}\n"
                f"Unit      : {r.unit_label}\n"
                f"Verification: {r.verification.status}\n"
            )
            if r.warnings:
                block += "Warnings  : " + "; ".join(r.warnings) + "\n"
            copy_to_clipboard(block)
        self.statusMessage.emit(f"Copied ({which})")

    def reset(self) -> None:
        self.input_field.clear()
        self._result = None
        self.grid.clear_values("-")
        self._set_alternatives_empty()
        self._clear_error()
        for btn in (self.copy_utc, self.copy_local, self.copy_full):
            btn.setEnabled(False)
        self.statusMessage.emit("New analysis")

    def load_value(self, value: str) -> None:
        self.input_field.setText(value)
        self.input_field.setFocus()
        self.run_analysis()