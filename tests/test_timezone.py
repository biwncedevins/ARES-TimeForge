"""Timezone handling tests (zoneinfo + tzdata on Windows)."""

import unittest
from datetime import datetime, timezone

from app.core import timezone as tz


class TestTimezone(unittest.TestCase):
    def test_utc_localize(self):
        aware, name, offset = tz.localize(
            datetime(2024, 5, 20, 10, 33, 54), "UTC"
        )
        self.assertEqual(name, "UTC")
        self.assertEqual(offset, "+00:00")
        self.assertEqual(
            aware.isoformat(), "2024-05-20T10:33:54+00:00"
        )

    def test_riyadh_offset(self):
        aware, name, offset = tz.localize(
            datetime(2024, 5, 20, 10, 33, 54), "Asia/Riyadh"
        )
        self.assertEqual(name, "Asia/Riyadh")
        self.assertEqual(offset, "+03:00")
        self.assertEqual(aware.hour, 13)

    def test_local_system(self):
        aware, name, offset = tz.localize(
            datetime(2024, 5, 20, 10, 33, 54), "Local"
        )
        self.assertEqual(name, "Local")
        self.assertTrue(aware.utcoffset() is not None)

    def test_unknown_zone_raises(self):
        with self.assertRaises(tz.TimeZoneError):
            tz.localize(datetime(2024, 1, 1), "Not/AZone")

    def test_dst_summer(self):
        aware, _name, offset = tz.localize(
            datetime(2024, 7, 1, 12, 0, 0), "America/New_York"
        )
        self.assertEqual(offset, "-04:00")

    def test_dst_winter(self):
        aware, _name, offset = tz.localize(
            datetime(2024, 1, 1, 12, 0, 0), "America/New_York"
        )
        self.assertEqual(offset, "-05:00")

    def test_presets_are_resolvable(self):
        for zone in tz.PRESET_ZONES:
            self.assertTrue(tz.is_known_zone(zone), zone)

    def test_from_local_ambiguous(self):
        # 2024-11-03 01:30 occurs twice (EDT and EST) in America/New_York.
        utc_result, note = tz.from_local_to_utc(
            datetime(2024, 11, 3, 1, 30, 0), "America/New_York"
        )
        self.assertIn("ambiguous", note)

    def test_from_local_gap(self):
        # 2024-03-10 02:30 does not exist in America/New_York.
        utc_result, note = tz.from_local_to_utc(
            datetime(2024, 3, 10, 2, 30, 0), "America/New_York"
        )
        self.assertIn("gap", note)

    def test_offset_str(self):
        self.assertEqual(tz.offset_str(tz.timezone(tz.timedelta(hours=3))), "+03:00")
        self.assertEqual(tz.offset_str(tz.timezone(-tz.timedelta(hours=4, minutes=30))), "-04:30")


if __name__ == "__main__":
    unittest.main()