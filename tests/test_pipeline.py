"""End-to-end pipeline tests."""

import unittest

from app.core.pipeline import AnalysisError, Pipeline


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline()

    def test_result_fields_populated(self):
        r = self.pipeline.analyze("1716201234567", "UTC")
        self.assertEqual(r.raw_value, "1716201234567")
        self.assertEqual(r.normalized_value, "1716201234567")
        self.assertEqual(r.format_name, "Unix Milliseconds")
        self.assertEqual(r.utc_str, "2024-05-20 10:33:54.567000")
        self.assertTrue(r.explanation)
        self.assertTrue(r.confidence_reasons)
        self.assertIn("1970-01-01", r.epoch_label)
        self.assertEqual(r.local_offset, "+00:00")
        self.assertIsNotNone(r.verification)

    def test_utc_is_authoritative(self):
        r1 = self.pipeline.analyze("1716201234567", "UTC")
        r2 = self.pipeline.analyze("1716201234567", "Asia/Riyadh")
        self.assertEqual(r1.utc_str, r2.utc_str)

    def test_nanosecond_precision_preserved(self):
        r = self.pipeline.analyze("1716201234567890123", "UTC")
        self.assertEqual(r.utc_str, "2024-05-20 10:33:54.567890123")
        self.assertEqual(r.fraction_display, "+123 ns")
        self.assertEqual(r.unix_ns, 1716201234567890123)

    def test_no_data_invented_before_input(self):
        r = self.pipeline.analyze("1716201234", "UTC")
        self.assertFalse(r.input_is_hex_notation)

    def test_raw_value_always_kept(self):
        r = self.pipeline.analyze("  0x01D71F0E96F4EBF0  ", "UTC")
        self.assertEqual(r.raw_value, "0x01D71F0E96F4EBF0")

    def test_alternatives_present_for_ambiguous(self):
        r = self.pipeline.analyze("742123456", "UTC")
        self.assertTrue(r.alternatives)

    def test_empty_input_raises_analysis_error(self):
        with self.assertRaises(AnalysisError):
            self.pipeline.analyze("", "UTC")

    def test_garbage_raises_analysis_error(self):
        with self.assertRaises(AnalysisError):
            self.pipeline.analyze("@@not-a-timestamp@@", "UTC")

    def test_as_dict_fields(self):
        r = self.pipeline.analyze("1716201234", "UTC")
        d = r.as_dict()
        for key in (
            "raw_value",
            "normalized_value",
            "detected_format",
            "confidence",
            "epoch",
            "unit",
            "utc",
            "local_time",
            "timezone",
            "offset",
            "verification",
            "warnings",
            "alternatives",
            "comparison",
        ):
            self.assertIn(key, d)


if __name__ == "__main__":
    unittest.main()