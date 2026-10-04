"""TimeForge — Forensic Timestamp Lab. Desktop, offline, Windows.

Entry point: run `python main.py` or execute the bundled TimeForge.exe.
"""

from __future__ import annotations

import sys
import traceback

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.ui.main_window import MainWindow
from app.ui.styles import STYLESHEET
from app.utils.resources import app_version, icon_path


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    detail = "".join(
        traceback.format_exception(exc_type, exc_value, exc_tb)
    )
    try:
        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("TimeForge — Unexpected Error")
        box.setText("Unhandled application error")
        box.setDetailedText(detail)
        box.exec()
    except Exception:  # pragma: no cover - best effort
        sys.stderr.write(detail)
    sys.exit(1)


def _run_selftest() -> int:
    """Lightweight bundled self-test; used to verify the frozen EXE."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from app.core.pipeline import AnalysisError, Pipeline

    pipeline = Pipeline()
    checks = [
        ("1716201234567", "unix_ms", None),
        ("1716201234", "unix_seconds", None),
        ("0x01D71F0E96F4EBF0", "filetime", None),
        ("45221.5", "ole", None),
        ("", None, AnalysisError),
        ("@@bad@", None, AnalysisError),
    ]
    for value, expected, exc_type in checks:
        if exc_type is not None:
            try:
                pipeline.analyze(value, "UTC")
                return 1
            except exc_type:
                continue
        result = pipeline.analyze(value, "UTC")
        if result.format_id != expected:
            return 1
    comparison = pipeline.compare("1716201234", "1716201234567", "UTC")
    if comparison.relation != "A BEFORE B":
        return 1
    print(f"selftest OK: {len(checks) - 2} conversions + error paths + compare")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return _run_selftest()
    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    app.setApplicationName("TimeForge")
    app.setApplicationVersion(app_version())
    app.setOrganizationName("TimeForge")
    app.setWindowIcon(QIcon(str(icon_path())))
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())