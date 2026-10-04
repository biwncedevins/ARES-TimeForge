"""GUI smoke tests (offscreen platform).

Exercises layout, visibility, page navigation, analyze / compare / export
flows, history, timezone switching and resize without a display server.
Skips cleanly when Qt cannot initialize.
"""

import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTableWidget,
)

try:
    _APP = QApplication.instance() or QApplication([])
    _QT_OK = True
except Exception:  # pragma: no cover
    _QT_OK = False

from app.formats import FORMATS
from app.ui.main_window import MainWindow


@unittest.skipUnless(_QT_OK, "Qt not available in this environment")
class TestGuiSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = _APP

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()

    # -- structure / layout ------------------------------------------
    def test_central_widget_is_set(self):
        self.assertIsNotNone(self.window.centralWidget())

    def test_stack_is_stackedwidget_with_6_pages(self):
        self.assertIsInstance(self.window.stack, QStackedWidget)
        self.assertEqual(self.window.stack.count(), 6)

    def test_all_pages_have_positive_size(self):
        for i in range(self.window.stack.count()):
            page = self.window.stack.widget(i)
            self.assertGreater(page.width(), 0, f"page {i} width")
            self.assertGreater(page.height(), 0, f"page {i} height")

    def test_no_zero_size_widgets(self):
        from PySide6.QtWidgets import QWidget as _QW

        def walk(widget, path=""):
            w, h = widget.width(), widget.height()
            self.assertGreaterEqual(w, 0, path)
            self.assertGreaterEqual(h, 0, path)
            for child in widget.children():
                if isinstance(child, _QW):
                    if not isinstance(child, QStackedWidget):
                        walk(child, f"{path}/{child.objectName() or child.__class__.__name__}")

        walk(self.window)

    def test_visibility_after_show(self):
        self.assertTrue(self.window.isVisible())
        self.assertTrue(self.window.sidebar.isVisible())
        self.assertTrue(self.window.topbar.isVisible())
        self.assertTrue(self.window.stack.isVisible())

    def test_sidebar_buttons(self):
        self.assertTrue(self.window.sidebar._buttons)
        for page_index, btn in self.window.sidebar._buttons.items():
            self.assertIsInstance(btn, QPushButton)
            self.assertTrue(btn.isCheckable())

    def test_topbar_buttons(self):
        for caption in ("New", "Analyze", "Compare", "Export"):
            self.assertIn(caption, self.window.topbar._buttons)

    def test_sidebar_navigation(self):
        for page_index in (1, 2, 3, 4, 5, 0):
            self.window._go_page(page_index)
            self.app.processEvents()
            self.assertEqual(
                self.window.stack.currentIndex(), page_index
            )

    # -- analyzer flow ---------------------------------------------------
    def test_analyze_populates_results(self):
        view = self.window.analyzer_view
        view.input_field.setText("1716201234567")
        view.run_analysis()
        self.app.processEvents()
        self.assertEqual(
            view.grid._rows["DETECTED FORMAT"].text(), "Unix Milliseconds"
        )
        self.assertEqual(
            view.grid._rows["UTC"].text(), "2024-05-20 10:33:54.567000"
        )
        self.assertTrue(view.copy_utc.isEnabled())

    def test_analyze_placeholders_before_input(self):
        view = self.window.analyzer_view
        self.assertEqual(view.grid._rows["INPUT"].text(), "-")
        self.assertEqual(view.grid._rows["UTC"].text(), "-")
        self.assertEqual(view.grid._rows["CONFIDENCE"].text(), "-")

    def test_analyze_invalid_shows_error_no_crash(self):
        view = self.window.analyzer_view
        view.input_field.setText("garbage @@")
        view.run_analysis()
        self.app.processEvents()
        self.assertTrue(view.error_label.isVisible())

    def test_analyze_empty_shows_error(self):
        view = self.window.analyzer_view
        view.run_analysis()
        self.app.processEvents()
        self.assertTrue(view.error_label.isVisible())

    def test_new_clears(self):
        view = self.window.analyzer_view
        view.input_field.setText("1716201234567")
        view.run_analysis()
        self.window._action_new()
        self.app.processEvents()
        self.assertEqual(view.input_field.text(), "")
        self.assertEqual(view.grid._rows["UTC"].text(), "-")

    def test_timezone_change_applied(self):
        view = self.window.analyzer_view
        view.input_field.setText("1716201234567")
        view.tz_combo.setCurrentText("Asia/Riyadh")
        view.run_analysis()
        self.app.processEvents()
        self.assertEqual(view.grid._rows["TIMEZONE"].text(), "Asia/Riyadh")
        self.assertEqual(view.grid._rows["OFFSET"].text(), "+03:00")

    def test_copy_buttons_enabled_after_analysis(self):
        view = self.window.analyzer_view
        view.input_field.setText("1716201234")
        view.run_analysis()
        self.app.processEvents()
        for btn in (view.copy_utc, view.copy_local, view.copy_full):
            self.assertTrue(btn.isEnabled())

    # -- compare flow ------------------------------------------------------
    def test_compare_works(self):
        view = self.window.compare_view
        view.a_field.setText("1716201234")
        view.b_field.setText("1716201234567")
        view.run_compare()
        self.app.processEvents()
        self.assertEqual(view.grid._rows["RELATION"].text(), "A BEFORE B")
        self.assertEqual(
            view.grid._rows["DIFFERENCE"].text(), "00:00:00.567000"
        )
        self.assertTrue(view.copy_result.isEnabled())

    def test_compare_requires_both(self):
        self.window._go_page(1)
        self.app.processEvents()
        view = self.window.compare_view
        view.a_field.setText("1716201234")
        view.b_field.setText("")
        view.run_compare()
        self.app.processEvents()
        self.assertTrue(view.error_label.isVisible())

    # -- formats page ------------------------------------------------------
    def test_formats_table_rows(self):
        view = self.window.formats_view
        self.assertEqual(view.table.rowCount(), len(FORMATS))
        self.assertIsInstance(view.table, QTableWidget)

    # -- history flow ------------------------------------------------------
    def test_history_after_analysis(self):
        self.window.analyzer_view.input_field.setText("1716201234")
        self.window.analyzer_view.run_analysis()
        self.app.processEvents()
        self.assertEqual(self.window.history_view.table.rowCount(), 1)

    def test_history_clear(self):
        self.window.analyzer_view.input_field.setText("1716201234")
        self.window.analyzer_view.run_analysis()
        self.app.processEvents()
        self.window.history_view._clear_history()
        self.app.processEvents()
        self.assertEqual(self.window.history_view.table.rowCount(), 0)

    def test_history_load_requests_value(self):
        captured = []
        self.window.history_view.loadRequested.disconnect()
        self.window.history_view.loadRequested.connect(
            lambda v: captured.append(v)
        )
        self.window.analyzer_view.input_field.setText("1716201234")
        self.window.analyzer_view.run_analysis()
        self.app.processEvents()
        self.window.history_view.table.selectRow(0)
        self.window.history_view._load_selected()
        self.assertEqual(captured, ["1716201234"])

    # -- export flow -------------------------------------------------------
    def test_export_json_to_disk(self):
        self.window.analyzer_view.input_field.setText("1716201234567")
        self.window.analyzer_view.run_analysis()
        self.app.processEvents()
        export = self.window.export_view
        export.format_combo.setCurrentIndex(export.format_combo.findData("json"))
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "out.json")
            export.path_field.setText(target)
            export._do_export()
            self.assertTrue(os.path.exists(target))
            import json

            with open(target, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["detected_format"], "Unix Milliseconds")

    def test_export_html_writes_local_file(self):
        self.window.analyzer_view.input_field.setText("1716201234567")
        self.window.analyzer_view.run_analysis()
        self.app.processEvents()
        export = self.window.export_view
        export.format_combo.setCurrentIndex(export.format_combo.findData("html"))
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "out.html")
            export.path_field.setText(target)
            export._do_export()
            with open(target, encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("<!doctype html>", content)
            self.assertIn("static format detection", content)

    # -- keyboards / sizes ------------------------------------------------
    def test_resize_works(self):
        self.window.resize(900, 600)
        self.app.processEvents()
        self.assertEqual(self.window.size().width(), 900)
        self.assertEqual(self.window.size().height(), 600)

    def test_stylesheet_applied(self):
        # MainWindow installs the stylesheet when the app has none.
        self.assertTrue(self.app.styleSheet().strip())
        self.assertIn("#080808", self.app.styleSheet())


if __name__ == "__main__":
    unittest.main()