"""Detection engine tests: confidence, candidates, ambiguity."""

import unittest

from app.core.detector import DetectionEngine, DetectionError


class TestDetection(unittest.TestCase):
    def setUp(self):
        self.engine = DetectionEngine()

    def test_no_candidates_for_moduleless_value(self):
        cands = self.engine.detect("9" * 40)
        self.assertEqual(cands, [])

    def test_unix_milliseconds_is_high_conf_leader(self):
        cands = self.engine.detect("1716201234567")
        self.assertTrue(cands)
        top = cands[0]
        self.assertEqual(top.format_id, "unix_ms")
        self.assertGreaterEqual(top.confidence, 75)
        self.assertEqual(top.confidence_level, "High")
        self.assertLessEqual(top.confidence, 100)

    def test_unix_seconds_detected(self):
        cands = self.engine.detect("1716201234")
        self.assertEqual(cands[0].format_id, "unix_seconds")

    def test_ambiguous_unix_vs_mac_lists_alternatives(self):
        cands = self.engine.detect("742123456")
        self.assertGreaterEqual(len(cands), 2)
        formats = {c.format_id for c in cands}
        self.assertIn("unix_seconds", formats)
        self.assertIn("mac_absolute", formats)
        self.assertTrue(cands[0].ambiguous)
        self.assertLess(cands[0].confidence, 100)

    def test_alternative_never_false_100_percent(self):
        for value in (
            "1716201234",
            "742123456",
            "1716201234567",
            "133432140000000000",
        ):
            cands = self.engine.detect(value)
            self.assertTrue(
                all(c.confidence < 100 for c in cands),
                f"candidate claimed 100% for {value}",
            )

    def test_hex_filetime_detected(self):
        cands = self.engine.detect("0x01D71F0E96F4EBF0")
        self.assertEqual(cands[0].format_id, "filetime")

    def test_ole_float_detected(self):
        cands = self.engine.detect("45221.5")
        self.assertEqual(cands[0].format_id, "ole")

    def test_confidence_helpers_present(self):
        cands = self.engine.detect("1716201234567")
        top = cands[0]
        self.assertIn(top.confidence_level, ("High", "Medium", "Low"))
        self.assertGreaterEqual(top.confidence, 0)
        self.assertLessEqual(top.confidence, 100)
        self.assertTrue(top.reasons)

    def test_invalid_input_raises_detection_error(self):
        with self.assertRaises(DetectionError):
            self.engine.detect("")


if __name__ == "__main__":
    unittest.main()