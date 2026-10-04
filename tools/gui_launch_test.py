"""On-screen launch check for the real TimeForge window.

Opens the actual desktop window (real platform, not offscreen), exercises
the layout, analysis, comparison and navigation flows through the UI, then
closes itself. Exit code 0 on success, 1 on any failure.

Usage:
    python tools/gui_launch_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.styles import STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()

    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)

    def run_checks() -> None:
        try:
            check("window visible", window.isVisible())
            check("sidebar visible", window.sidebar.isVisible())
            check("topbar visible", window.topbar.isVisible())
            check("stack visible", window.stack.isVisible())
            check("6 pages", window.stack.count() == 6)

            view = window.analyzer_view
            view.input_field.setText("1716201234567")
            view.run_analysis()
            app.processEvents()
            check(
                "analysis format",
                view.grid._rows["DETECTED FORMAT"].text() == "Unix Milliseconds",
            )
            check(
                "analysis utc",
                view.grid._rows["UTC"].text() == "2024-05-20 10:33:54.567000",
            )
            check("copy buttons enabled", view.copy_utc.isEnabled())

            idx = view.tz_combo.findText("Asia/Riyadh")
            check("timezone available", idx >= 0)
            view.tz_combo.setCurrentIndex(idx)
            view.run_analysis()
            app.processEvents()
            u = view.grid._rows["UTC"].text()
            ln = view.grid._rows["LOCAL TIME"].text()
            of = view.grid._rows["OFFSET"].text()
            check("utc still authoritative", u == "2024-05-20 10:33:54.567000")
            check("local shifted +03", ln == "2024-05-20 13:33:54.567000 +03:00")
            check("offset tag", of == "+03:00")
            view.tz_combo.setCurrentIndex(view.tz_combo.findText("Local"))

            window._go_page(1)
            app.processEvents()
            cv = window.compare_view
            cv.a_field.setText("1716201234")
            cv.b_field.setText("1716201234567")
            cv.run_compare()
            app.processEvents()
            check(
                "compare relation",
                cv.grid._rows["RELATION"].text() == "A BEFORE B",
            )

            window._go_page(2)
            app.processEvents()
            check("formats rows", window.formats_view.table.rowCount() >= 9)

            window._go_page(3)
            app.processEvents()
            check("history rows", window.history_view.table.rowCount() >= 1)

            window._go_page(0)
            check("sized", window.size().width() >= 880)
            window.resize(980, 640)
            app.processEvents()
            check("center visible", window.centralWidget().isVisible())
            window.resize(1320, 820)
            app.processEvents()
            check("center visible2", window.centralWidget().isVisible())
            check("central widget", window.centralWidget() is not None)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"exception: {exc!r}")

        if failures:
            print("ONSCREEN FAIL:", " ; ".join(failures))
            app.exit(1)
        else:
            print("ONSCREEN OK")
            app.exit(0)

    QTimer.singleShot(1500, run_checks)
    QTimer.singleShot(12000, lambda: app.exit(2))
    rc = app.exec()
    window.close()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())