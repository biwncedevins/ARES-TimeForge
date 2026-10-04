"""Deterministic conversion tests for every supported format."""

import unittest
from datetime import datetime

from app.formats import FORMAT_BY_ID, ConversionError


def utc(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


class TestFormatConversions(unittest.TestCase):
    def assert_converts(self, fmt_id, value, expected_iso, remainder=0):
        dt, rem, _ns = FORMAT_BY_ID[fmt_id].convert(value)
        self.assertEqual(dt, utc(expected_iso), fmt_id)
        self.assertEqual(rem, remainder, f"{fmt_id} nanosecond remainder")

    def test_unix_seconds(self):
        self.assert_converts("unix_seconds", 0, "1970-01-01T00:00:00")
        self.assert_converts("unix_seconds", 1, "1970-01-01T00:00:01")
        self.assert_converts(
            "unix_seconds", 1716201234, "2024-05-20T10:33:54"
        )

    def test_unix_milliseconds(self):
        self.assert_converts(
            "unix_ms", 1716201234567, "2024-05-20T10:33:54.567000"
        )

    def test_unix_microseconds(self):
        self.assert_converts(
            "unix_us", 1716201234567890, "2024-05-20T10:33:54.567890"
        )

    def test_unix_nanoseconds_preserves_sub_micro(self):
        dt, rem, ns = FORMAT_BY_ID["unix_ns"].convert(1716201234567890123)
        self.assertEqual(dt, utc("2024-05-20T10:33:54.567890"))
        self.assertEqual(rem, 123)
        self.assertEqual(ns, 1716201234567890123)

    def test_filetime(self):
        self.assert_converts("filetime", 0, "1601-01-01T00:00:00")
        self.assert_converts(
            "filetime", 116444736000000000, "1970-01-01T00:00:00"
        )
        self.assert_converts(
            "filetime", 132609749535576000, "2021-03-23T12:09:13.557600"
        )

    def test_dotnet_ticks(self):
        self.assert_converts("dotnet_ticks", 0, "0001-01-01T00:00:00")
        self.assert_converts(
            "dotnet_ticks", 621355968000000000, "1970-01-01T00:00:00"
        )

    def test_chromium_and_webkit_share_epoch(self):
        self.assert_converts(
            "chromium", 11644473600000000, "1970-01-01T00:00:00"
        )
        self.assert_converts(
            "webkit", 11644473600000000, "1970-01-01T00:00:00"
        )

    def test_mac_absolute(self):
        self.assert_converts("mac_absolute", 0, "2001-01-01T00:00:00")
        self.assert_converts("mac_absolute", -978307200, "1970-01-01T00:00:00")
        self.assert_converts(
            "mac_absolute", 742123456, "2024-07-08T09:24:16"
        )

    def test_ole(self):
        self.assert_converts("ole", 0, "1899-12-30T00:00:00")
        self.assert_converts("ole", 2.0, "1900-01-01T00:00:00")
        self.assert_converts("ole", 45221.5, "2023-10-22T12:00:00")


class TestConversionErrors(unittest.TestCase):
    def test_year_overflow_raises(self):
        with self.assertRaises(ConversionError):
            FORMAT_BY_ID["unix_seconds"].convert(10 ** 30)

    def test_ole_out_of_range(self):
        with self.assertRaises(ConversionError):
            FORMAT_BY_ID["ole"].convert(-800000.0)
        with self.assertRaises(ConversionError):
            FORMAT_BY_ID["ole"].convert(3000000.0)


if __name__ == "__main__":
    unittest.main()