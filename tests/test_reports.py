"""Report export tests (JSON / CSV / TXT / HTML)."""

import json
import tempfile
import unittest
from pathlib import Path

from app.core.pipeline import Pipeline
from app.reports import render


class TestReports(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline()
        self.result = self.pipeline.analyze("1716201234567", "UTC")
        self.comparison = self.pipeline.compare(
            "1716201234", "1716201234567", "UTC"
        )

    def test_json_valid_and_structured(self):
        text = render("json", [self.result], None)
        data = json.loads(text)
        self.assertEqual(data["raw_value"], "1716201234567")
        self.assertEqual(data["detected_format"], "Unix Milliseconds")
        self.assertEqual(data["confidence"], 75)
        self.assertIn("alternatives", data)
        self.assertIn("verification", data)
        self.assertIn("comparison", data)

    def test_json_comparison(self):
        text = render("json", [], self.comparison)
        data = json.loads(text)
        self.assertEqual(data["comparison"]["relation"], "A BEFORE B")
        self.assertEqual(
            data["comparison"]["difference"], "00:00:00.567000"
        )

    def test_csv_headers(self):
        text = render("csv", [self.result], None)
        header = text.splitlines()[0]
        for field in ("raw_value", "detected_format", "utc", "local_time"):
            self.assertIn(field, header.split(","))

    def test_txt_forensic_section(self):
        text = render("txt", [self.result], None)
        self.assertIn("TIMEFORGE | Forensic Timestamp Lab", text)
        self.assertIn("INPUT", text)
        self.assertIn("WHY SELECTED", text)
        self.assertIn("should be validated against the source artifact", text)

    def test_html_disclaimer_and_escaped(self):
        tricky = self.pipeline.analyze("1716201234", "UTC")
        text = render("html", [tricky], None)
        self.assertIn(
            "Timestamp interpretation is based on static format detection",
            text,
        )
        self.assertIn("<!doctype html>", text)
        self.assertIn("<table>", text)
        self.assertNotIn("http://", text)
        self.assertNotIn("https://", text)

    def test_html_escapes_special_input(self):
        html_text = render("html", [self.result], None)
        self.assertNotIn("<script>", html_text)

    def test_history_export(self):
        self.pipeline.analyze("1716201234", "UTC")
        text = render("json", [self.result], self.comparison)
        data = json.loads(text)
        self.assertIn("comparison", data)

    def test_write_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            content = render("json", [self.result], None)
            path.write_text(content, encoding="utf-8")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["detected_format"], "Unix Milliseconds")


if __name__ == "__main__":
    unittest.main()