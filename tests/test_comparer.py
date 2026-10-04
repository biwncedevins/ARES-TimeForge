"""Comparison engine tests."""

import unittest

from app.core.pipeline import Pipeline


class TestComparison(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline()

    def test_a_before_b(self):
        c = self.pipeline.compare("1716201234", "1716201234567", "UTC")
        self.assertEqual(c.relation, "A BEFORE B")
        self.assertEqual(c.a_utc, "2024-05-20 10:33:54")
        self.assertEqual(c.b_utc, "2024-05-20 10:33:54.567000")
        self.assertEqual(c.difference, "00:00:00.567000")
        self.assertFalse(c.equal)

    def test_a_after_b(self):
        c = self.pipeline.compare("1716201234567", "1716201234", "UTC")
        self.assertEqual(c.relation, "A AFTER B")

    def test_same_time(self):
        c = self.pipeline.compare("1716201234", "1716201234", "UTC")
        self.assertEqual(c.relation, "SAME TIME")
        self.assertTrue(c.equal)
        self.assertEqual(c.difference, "00:00:00")

    def test_nanosecond_precision_ordering(self):
        c = self.pipeline.compare(
            "1716201234567890122", "1716201234567890123", "UTC"
        )
        self.assertEqual(c.relation, "A BEFORE B")

    def test_two_day_diff(self):
        c = self.pipeline.compare("1716201234", "1716374034", "UTC")
        self.assertEqual(c.relation, "A BEFORE B")
        self.assertEqual(c.difference, "2 day(s), 00:00:00")

    def test_compare_failure_propagates(self):
        from app.core.pipeline import AnalysisError

        with self.assertRaises(AnalysisError):
            self.pipeline.compare("garbage", "1716201234", "UTC")


if __name__ == "__main__":
    unittest.main()