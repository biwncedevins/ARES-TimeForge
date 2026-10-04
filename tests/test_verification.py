"""Verification engine tests."""

import unittest

from app.core.pipeline import AnalysisError, Pipeline
from app.models.verification import INVALID, VALID, WARNING


class TestVerification(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline()

    def test_valid_modern_timestamp_is_valid(self):
        result = self.pipeline.analyze("1716201234567", "UTC")
        self.assertEqual(result.verification.status, VALID)

    def test_negative_filetime_invalid(self):
        result = self.pipeline.analyze("-100000000000000000", "UTC")
        self.assertEqual(result.verification.status, INVALID)
        self.assertTrue(
            any("FILETIME" in m.text for m in result.verification.messages)
        )

    def test_future_date_warns(self):
        # A FILETIME value resolving to ~year 2995 -> warning for being
        # outside the expected forensic analysis range.
        value = 440000000000000000
        result = self.pipeline.analyze(str(value), "UTC")
        self.assertEqual(result.verification.status, WARNING)
        self.assertTrue(result.warnings)

    def test_overflow_raises_and_is_caught(self):
        with self.assertRaises(AnalysisError):
            self.pipeline.analyze("9" * 40, "UTC")

    def test_negative_unix_warns_not_invalid(self):
        result = self.pipeline.analyze("-1", "UTC")
        self.assertEqual(result.verification.status, WARNING)

    def test_no_verdicts_like_malicious(self):
        result = self.pipeline.analyze("-1", "UTC")
        text = " ".join(m.text for m in result.verification.messages).lower()
        self.assertNotIn("malicious", text)
        self.assertNotIn("benign", text)


if __name__ == "__main__":
    unittest.main()